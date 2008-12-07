#!/usr/bin/perl
# Handles remote_* function calls by a faster method. When first called
# as a CGI, forks and starts listening on a port which is returned to the
# client. From then on, direct TCP connections can be made to this port
# to send requests and get replies.

do './web-lib.pl';
use POSIX;
use Socket;
$force_lang = $default_lang;
&init_config();
print "Content-type: text/plain\n\n";

# Can this user make remote calls?
%access = &get_module_acl();
if ($access{'rpc'} == 0 || $access{'rpc'} == 2 &&
    $base_remote_user ne 'admin' && $base_remote_user ne 'root') {
	print "0 Invalid user for RPC\n";
	exit;
	}

# Find a free port
&get_miniserv_config(\%miniserv);
$port = $miniserv{'port'} || 10000;
$aerr = &allocate_socket(MAIN, \$port);
if ($aerr) {
	print "0 $aerr\n";
	exit;
	}
if (open(RANDOM, "/dev/urandom")) {
	local $tmpsid;
	read(RANDOM, $tmpsid, 16);
	$sid = lc(unpack('h*', $tmpsid));
	close RANDOM;
	}
else {
	$sid = time()*$$;
	}
$version = &get_webmin_version();
print "1 $port $sid $version\n";

# Fork and listen for calls ..
$pid = fork();
if ($pid < 0) {
	die "fork() failed : $!";
	}
elsif ($pid) {
	exit;
	}
untie(*STDIN);
untie(*STDOUT);

# Accept the TCP connection
$acptaddr = accept(SOCK, MAIN);
die "accept failed!" if (!$acptaddr);
select(SOCK); $| = 1;

while(1) {
	# Wait for the request
	local $rmask;
	vec($rmask, fileno(SOCK), 1) = 1;
	local $sel = select($rmask, undef, undef, 30);
	last if ($sel <= 0);

	local $line = <SOCK>;
	last if (!$line);
	local ($len, $auth) = split(/\s+/, $line);
	die "Invalid session ID" if ($auth ne $sid);
	local $rawarg;
	while(length($rawarg) < $len) {
		local $got;
		local $rv = read(SOCK, $got, $len - length($rawarg));
		exit if ($rv <= 0);
		$rawarg .= $got;
		}
	print STDERR "fastrpc: raw $rawarg\n" if ($gconfig{'rpcdebug'});
	local $arg = &unserialise_variable($rawarg);

	# Process it
	local $rawrv;
	if ($arg->{'action'} eq 'ping') {
		# Just respond with an OK
		print STDERR "fastrpc: ping\n" if ($gconfig{'rpcdebug'});
		$rawrv = &serialise_variable( { 'status' => 1 } );
		}
	elsif ($arg->{'action'} eq 'check') {
		# Check if some module is supported
		print STDERR "fastrpc: check $arg->{'module'}\n" if ($gconfig{'rpcdebug'});
		$rawrv = &serialise_variable(
			{ 'status' => 1,
			  'rv' => &foreign_check($arg->{'module'}) } );
		}
	elsif ($arg->{'action'} eq 'config') {
		# Get the config for some module
		print STDERR "fastrpc: config $arg->{'module'}\n" if ($gconfig{'rpcdebug'});
		local %config = &foreign_config($arg->{'module'});
		$rawrv = &serialise_variable(
			{ 'status' => 1, 'rv' => \%config } );
		}
	elsif ($arg->{'action'} eq 'write') {
		# Transfer data to a local temp file
		local $file = $arg->{'file'} ? $arg->{'file'} : &tempname();
		print STDERR "fastrpc: write $file\n" if ($gconfig{'rpcdebug'});
		open(FILE, ">$file");
		print FILE $arg->{'data'};
		close(FILE);
		$rawrv = &serialise_variable(
			{ 'status' => 1, 'rv' => $file } );
		}
	elsif ($arg->{'action'} eq 'tcpwrite') {
		# Transfer data to a local temp file over TCP connection
		local $file = $arg->{'file'} ? $arg->{'file'} : &tempname();
		print STDERR "fastrpc: tcpwrite $file\n" if ($gconfig{'rpcdebug'});
		local $tsock = time().$$;
		local $tport = $port + 1;
		&allocate_socket($tsock, \$tport);
		if (!fork()) {
			# Accept connection in separate process
			local $rmask;
			vec($rmask, fileno($tsock), 1) = 1;
			local $sel = select($rmask, undef, undef, 30);
			exit if ($sel <= 0);
			accept(TRANS, $tsock) || exit;
			local $buf;
			open(FILE, ">$file");
			while(read(TRANS, $buf, 1024) > 0) {
				print FILE $buf;
				}
			close(FILE);
			close(TRANS);
			exit;
			}
		close($tsock);
		print STDERR "fastrpc: tcpwrite $file done\n" if ($gconfig{'rpcdebug'});
		$rawrv = &serialise_variable(
			{ 'status' => 1, 'rv' => [ $file, $tport ] } );
		}
	elsif ($arg->{'action'} eq 'read') {
		# Transfer data from a file
		print STDERR "fastrpc: read $arg->{'file'}\n" if ($gconfig{'rpcdebug'});
		local ($data, $got);
		open(FILE, $arg->{'file'});
		while(read(FILE, $got, 1024) > 0) {
			$data .= $got;
			}
		close(FILE);
		$rawrv = &serialise_variable(
			{ 'status' => 1, 'rv' => $data } );
		}
	elsif ($arg->{'action'} eq 'tcpread') {
		# Transfer data from a file over TCP connection
		print STDERR "fastrpc: tcpread $arg->{'file'}\n" if ($gconfig{'rpcdebug'});
		local $tsock = time().$$;
		local $tport = $port + 1;
		&allocate_socket($tsock, \$tport);
		if (!fork()) {
			# Accept connection in separate process
			local $rmask;
			vec($rmask, fileno($tsock), 1) = 1;
			local $sel = select($rmask, undef, undef, 30);
			exit if ($sel <= 0);
			accept(TRANS, $tsock) || exit;
			local $buf;
			open(FILE, $arg->{'file'});
			while(read(FILE, $buf, 1024) > 0) {
				print TRANS $buf;
				}
			close(FILE);
			close(TRANS);
			exit;
			}
		close($tsock);
		print STDERR "fastrpc: tcpread $arg->{'file'} done\n" if ($gconfig{'rpcdebug'});
		$rawrv = &serialise_variable(
			{ 'status' => 1, 'rv' => [ $arg->{'file'}, $tport ] } );
		}
	elsif ($arg->{'action'} eq 'require') {
		# require a library
		print STDERR "fastrpc: require $arg->{'module'}/$arg->{'file'}\n" if ($gconfig{'rpcdebug'});
		&foreign_require($arg->{'module'},
				 $arg->{'file'});
		$rawrv = &serialise_variable( { 'status' => 1 });
		}
	elsif ($arg->{'action'} eq 'call') {
		# execute a function
		print STDERR "fastrpc: call $arg->{'module'}::$arg->{'func'}(",join(",", @{$arg->{'args'}}),")\n" if ($gconfig{'rpcdebug'});
		local @rv = &foreign_call($arg->{'module'},
				    $arg->{'func'},
				    @{$arg->{'args'}});
		if (@rv == 1) {
			$rawrv = &serialise_variable(
				{ 'status' => 1, 'rv' => $rv[0] } );
			}
		else {
			$rawrv = &serialise_variable(
				{ 'status' => 1, 'arv' => \@rv } );
			}
		print STDERR "fastrpc: call $arg->{'module'}::$arg->{'func'} done = ",join(",", @rv),"\n" if ($gconfig{'rpcdebug'});
		}
	elsif ($arg->{'action'} eq 'eval') {
		# eval some perl code
		print STDERR "fastrpc: eval $arg->{'module'} $arg->{'code'}\n" if ($gconfig{'rpcdebug'});
		local $rv;
		if ($arg->{'module'}) {
			$rv = eval "package $arg->{'module'};\n".
				   $arg->{'code'}."\n";
			}
		else {
			$rv = eval $arg->{'code'};
			}
		print STDERR "fastrpc: eval $arg->{'module'} $arg->{'code'} done = $rv\n" if ($gconfig{'rpcdebug'});
		$rawrv = &serialise_variable(
			{ 'status' => 1, 'rv' => $rv } );
		}
	elsif ($arg->{'action'} eq 'quit') {
		print STDERR "fastrpc: quit\n" if ($gconfig{'rpcdebug'});
		$rawrv = &serialise_variable( { 'status' => 1 } );
		}
	else {
		print STDERR "fastrpc: unknown $arg->{'action'}\n" if ($gconfig{'rpcdebug'});
		$rawrv = &serialise_variable( { 'status' => 0 } );
		}

	# Send back to the client
	print SOCK length($rawrv),"\n";
	print SOCK $rawrv;
	last if ($arg->{'action'} eq 'quit');
	}

# allocate_socket(handle, &port)
sub allocate_socket
{
local $fh = $_[0];
local $proto = getprotobyname('tcp');
if (!socket($fh, PF_INET, SOCK_STREAM, $proto)) {
	return "socket failed : $!";
	}
setsockopt($fh, SOL_SOCKET, SO_REUSEADDR, pack("l", 1));
while(1) {
	${$_[1]}++;
	last if (bind($fh, sockaddr_in(${$_[1]}, INADDR_ANY)));
	}
listen($fh, SOMAXCONN);
return undef;
}

