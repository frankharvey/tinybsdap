#!/usr/bin/perl
# save_options.cgi
# Save client options for some subnet, shared net, group, host or global

require './dhcpd-lib.pl';
require './params-lib.pl';
&ReadParse();
&lock_file($config{'dhcpd_conf'});
$client = &get_parent_config();
foreach $i ($in{'sidx'}, $in{'uidx'}, $in{'gidx'}, $in{'idx'}) {
	if ($i ne '') {
		$client = $client->{'members'}->[$i];
		$indent++;
		}
	}

# check acls
%access = &get_module_acl();
&error_setup("<blink><font color=red>$text{'eacl_aviol'}</font></blink>");
if ($client->{'name'} eq 'subnet') {
	&error("$text{'eacl_np'} $text{'eacl_pus'}")
		if !&can('rw', \%access, $client);
	}
elsif ($client->{'name'} eq 'shared-network') {
	&error("$text{'eacl_np'} $text{'eacl_pun'}")
		if !&can('rw', \%access, $client);
	}
elsif ($client->{'name'} eq 'host') {
	&error("$text{'eacl_np'} $text{'eacl_puh'}")
		if !&can('rw', \%access, $client);
	}
elsif ($client->{'name'} eq 'group') {
	&error("$text{'eacl_np'} $text{'eacl_pug'}")
		if !&can('rw', \%access, $client);
	}
else {
	&error("$text{'eacl_np'} $text{'eacl_pglob'}")
		if !$access{'global'};
	}

# save
&error_setup($text{'sopt_failsave'});

&save_option("host-name", 3, $client, $indent);
&save_option("routers", 2, $client, $indent);
&save_option("subnet-mask", 0, $client, $indent);
&save_option("broadcast-address", 0, $client, $indent);
&save_option("domain-name", 3, $client, $indent);
&save_option("domain-name-servers", 2, $client, $indent);
&save_option("time-servers", 2, $client, $indent);
&save_option("log-servers", 2, $client, $indent);
&save_option("swap-server", 2, $client, $indent);
&save_option("root-path", 3, $client, $indent);
&save_option("nis-domain", 3, $client, $indent);
&save_option("nis-servers", 2, $client, $indent);
&save_option("font-servers", 2, $client, $indent);
&save_option("x-display-manager", 2, $client, $indent);
&save_option("static-routes", 5, $client, $indent);
&save_option("ntp-servers", 2, $client, $indent);
&save_option("netbios-name-servers", 2, $client, $indent);
&save_option("netbios-scope", 3, $client, $indent);
&save_option("netbios-node-type", 1, $client, $indent);
&save_option("time-offset", 1, $client, $indent);
if ($in{'level'} eq "global") {
	# save params as well
	&save_choice("use-host-decl-names", $client, 0);
	&parse_params($client, 0);
	}
elsif ($in{'level'} eq "host") {
	$ret="edit_host.cgi?sidx=$in{'sidx'}&uidx=$in{'uidx'}&gidx=$in{'gidx'}&idx=$in{'idx'}";
	}
elsif ($in{'level'} eq "group") {
	$ret="edit_group.cgi?sidx=$in{'sidx'}&uidx=$in{'uidx'}&idx=$in{'idx'}";
	}
elsif ($in{'level'} eq "subnet") {
	$ret="edit_subnet.cgi?sidx=$in{'sidx'}&idx=$in{'idx'}";
	}
elsif ($in{'level'} eq "shared-network") {
	$ret="edit_shared.cgi?idx=$in{'idx'}";
	}

# save custom options
@custom = grep { $_->{'name'} eq 'option' &&
		 $_->{'values'}->[0] =~ /^option-(\d+)$/ &&
		 $_->{'values'}->[1] ne 'code' }
	       @{$client->{'members'}};
for($i=0; defined($in{"cnum_$i"}); $i++) {
	next if (!$in{"cnum_$i"} || !$in{"cval_$i"});
	$in{"cnum_$i"} =~ /^\d+$/ ||
		&error(&text('sopt_invalidnum', $in{"cnum_$i"}));
	local $cv = $in{"cval_$i"};
	$cv = "\"$cv\"" if ($cv !~ /^([0-9a-fA-F]{1,2}:)*[0-9a-fA-F]{1,2}$/);
	push(@newcustom, { 'name' => 'option',
			   'values' => [ 'option-'.$in{"cnum_$i"},
					 $cv ] } );
	}
&save_directive($client, \@custom, \@newcustom, $indent, 1);

if ($config{'dhcpd_version'} >= 3) {
	# save option definitions
	@defs = grep { $_->{'name'} eq 'option' &&
			 $_->{'values'}->[1] eq 'code' &&
			 $_->{'values'}->[3] eq '=' }
		       @{$client->{'members'}};
	for($i=0; defined($in{"dname_$i"}); $i++) {
		next if (!$in{"dname_$i"} || !$in{"dnum_$i"} ||
			 !$in{"dtype_$i"});
		$in{"dname_$i"} =~ /^[a-z0-9\.\-\_]+$/i ||
			&error(&text('sopt_edname', $in{"dname_$i"}));
		$in{"dnum_$i"} =~ /^\d+$/ ||
			&error(&text('sopt_ednum', $in{"dnum_$i"}));
		$in{"dtype_$i"} =~ /^[a-z0-9\.\-\_]+$/i ||
			&error(&text('sopt_edtype', $in{"dtype_$i"}));
		push(@newdefs, { 'name' => 'option',
				 'values' => [ $in{"dname_$i"}, "code",
					       $in{"dnum_$i"}, "=",
					       $in{"dtype_$i"}
					     ] } );
		}
	&save_directive($client, \@defs, \@newdefs, $indent, 1);
	}

&flush_file_lines();
&unlock_file($config{'dhcpd_conf'});
if ($client->{'name'} eq 'subnet') {
	&webmin_log("options", 'subnet',
		    "$client->{'values'}->[0]/$client->{'values'}->[2]", \%in);
	}
elsif ($client->{'name'} eq 'shared-network') {
	&webmin_log("options", 'subnet', $client->{'values'}->[0], \%in);
	}
elsif ($client->{'name'} eq 'host') {
	&webmin_log("options", 'host', $client->{'values'}->[0], \%in);
	}
elsif ($client->{'name'} eq 'group') {
	@count = &find("host", $client->{'members'});
	&webmin_log("options", 'group',
		    join(",", map { $_->{'values'}->[0] } @count), \%in);
	}
&redirect($ret);

# save_option(name, type, &config, indent)
sub save_option
{
local($v);
local $m = $_[2]->{'members'};
for($i=0; $i<@$m; $i++) {
	if ($m->[$i]->{'name'} eq 'option' &&
	    $m->[$i]->{'values'}->[0] eq $_[0]) {
		$v = $m->[$i];
		last;
		}
	}
if ($in{"$_[0]_def"}) {
	&save_directive($_[2], [ $v ], [ ], 0, 1) if ($v);
	}
else {
	local $nv = $in{$_[0]};
	local @nv = split(/\s+/, $nv);
	if ($_[1] == 0) {
		gethostbyname($nv) || &check_ipaddress($nv) ||
			&error("$_[0] '$nv' $text{'sopt_invalidip'}");
		}
	elsif ($_[1] == 1) {
		$nv =~ /^-?\d+$/ || &error("'$nv' $text{'sopt_invalidint'}");
		}
	elsif ($_[1] == 2) {
		local $ip;
		foreach $ip (@nv) {
			gethostbyname($ip) || &check_ipaddress($ip) ||
				&error("'$ip' $text{'sopt_invalidip'}");
			}
		$nv = join(", ", @nv);
		}
	elsif ($_[1] == 3) {
		$nv = "\"$nv\"";
		}
	elsif ($_[1] == 5) {
		local($ipp, @nnv);
		foreach $ipp (@nv) {
			$ipp =~ /^(\S+)\s*,\s*(\S+)$/ ||
				&error("'$ipp' $text{'sopt_invalidipp'}");
			&check_ipaddress($1) ||
				&error("'$1' $text{'sopt_invalidip'}");
			&check_ipaddress($2) ||
				&error("'$2' $text{'sopt_invalidip'}");
			push(@nnv, "$1 $2");
			}
		$nv = join(", ", @nnv);
		}
	local $dir = { 'name' => 'option',
		       'values' => [ $_[0], $nv ] };
	&save_directive($_[2], $v ? [ $v ] : [ ], [ $dir ], $_[3], 1);
	}
}

