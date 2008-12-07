#!/usr/local/bin/perl
# change_bind.cgi
# Update the binding IP address and port for miniserv

require './webmin-lib.pl';
use Socket;
&ReadParse();
&get_miniserv_config(\%miniserv);
%oldminiserv = %miniserv;
&error_setup($text{'bind_err'});

# Validate inputs
for($i=0; defined($in{"ip_def_$i"}); $i++) {
	next if (!$in{"ip_def_$i"});
	if ($in{"ip_def_$i"} == 1) {
		$ip = "*";
		}
	else {
		$ip = $in{"ip_$i"};
		&check_ipaddress($ip) || &error(&text('bind_eip2', $ip));
		}
	if ($in{"port_def_$i"} == 1) {
		$port = $in{"port_$i"};
		$port =~ /^\d+$/ && $port < 65536 ||
			&error(&text('bind_eport2', $port));
		}
	else {
		$port = "*";
		}
	push(@sockets, [ $ip, $port ]);
	}
@sockets || &error($text{'bind_enone'});
$in{'listen_def'} || $in{'listen'} =~ /^\d+$/ || &error($text{'bind_elisten'});

# Update config file
&lock_file($ENV{'MINISERV_CONFIG'});
$first = shift(@sockets);
$miniserv{'port'} = $first->[1];
if ($first->[0] eq "*") {
	delete($miniserv{'bind'});
	}
else {
	$miniserv{'bind'} = $first->[0];
	}
$miniserv{'sockets'} = join(" ", map { "$_->[0]:$_->[1]" } @sockets);
if ($in{'listen_def'}) {
	delete($miniserv{'listen'});
	}
else {
	$miniserv{'listen'} = $in{'listen'};
	}
&put_miniserv_config(\%miniserv);
&unlock_file($ENV{'MINISERV_CONFIG'});

# Attempt to re-start miniserv
$SIG{'TERM'} = 'ignore';
&system_logged("$config_directory/stop >/dev/null 2>&1 </dev/null");
$temp = &tempname();
$rv = &system_logged("$config_directory/start >$temp 2>&1 </dev/null");
$out = `cat $temp`;
$out =~ s/^Starting Webmin server in.*\n//;
$out =~ s/at.*line.*//;
unlink($temp);
if ($rv) {
	# Failed! Roll back config and start again
	&lock_file($ENV{'MINISERV_CONFIG'});
	&put_miniserv_config(\%oldminiserv);
	&unlock_file($ENV{'MINISERV_CONFIG'});
	&system_logged("$config_directory/start >/dev/null 2>&1 </dev/null");
	&error(&text('bind_erestart', $out));
	}
&webmin_log("bind", undef, undef, \%in);

if ($miniserv{'bind'}) { $url = $miniserv{'bind'}; }
else { $url = $ENV{'SERVER_NAME'}; }
$url .= ":$miniserv{'port'}/webmin/";
if ($ENV{'HTTPS'} eq "ON") { &redirect("https://$url"); }
else { &redirect("http://$url"); }

