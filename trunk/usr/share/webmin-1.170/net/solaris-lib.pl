# solaris-lib.pl
# Networking functions for solaris

$min_virtual_number = 1;

# active_interfaces()
# Returns a list of currently ifconfig'd interfaces
sub active_interfaces
{
local(@rv, @lines, $l);
open(IFC, "ifconfig -a |");
while(<IFC>) {
	s/\r|\n//g;
	if (/^\S+:/) { push(@lines, $_); }
	else { $lines[$#lines] .= $_; }
	}
close(IFC);
foreach $l (@lines) {
	local %ifc;
	$l =~ /^([^:\s]+):/; $ifc{'name'} = $1;
	$l =~ /^(\S+):/; $ifc{'fullname'} = $1;
	if ($l =~ /^(\S+):(\d+):\s/) { $ifc{'virtual'} = $2; }
	if ($l =~ /inet\s+(\S+)/) { $ifc{'address'} = $1; }
	if ($l =~ /netmask\s+(\S+)/) { $ifc{'netmask'} = &parse_hex($1); }
	if ($l =~ /broadcast\s+(\S+)/) { $ifc{'broadcast'} = $1; }
	if ($l =~ /ether\s+(\S+)/) { $ifc{'ether'} = $1; }
	if ($l =~ /mtu\s+(\S+)/) { $ifc{'mtu'} = $1; }
	$ifc{'up'}++ if ($l =~ /\<UP/);
	$ifc{'edit'} = ($ifc{'name'} !~ /ipdptp|ppp/);
	$ifc{'index'} = scalar(@rv);
	if ($ifc{'ether'}) {
		$ifc{'ether'} = join(":", map { sprintf "%2.2X", hex($_) }
					      split(/:/, $ifc{'ether'}));
		}
	push(@rv, \%ifc);
	}
return @rv;
}

# activate_interface(&details)
# Create or modify an interface
sub activate_interface
{
local $a = $_[0];
if ($a->{'virtual'} eq "") {
	local $out = &backquote_logged("ifconfig $a->{'name'} plumb 2>&1");
	if ($out) { &error(&text('aifc_eexist', $a->{'name'})); }
	}
elsif ($gconfig{'os_version'} >= 8) {
	&system_logged("ifconfig $a->{'name'}:$a->{'virtual'} plumb >/dev/null 2>&1");
	}
local $cmd = "ifconfig $a->{'name'}";
if ($a->{'virtual'} ne "") { $cmd .= ":$a->{'virtual'}"; }
$cmd .= " $a->{'address'}";
if ($a->{'netmask'}) { $cmd .= " netmask $a->{'netmask'}"; }
else { $cmd .= " netmask +"; }
if ($a->{'broadcast'}) { $cmd .= " broadcast $a->{'broadcast'}"; }
else { $cmd .= " broadcast +"; }
if ($a->{'mtu'}) { $cmd .= " mtu $a->{'mtu'}"; }
if ($a->{'up'}) { $cmd .= " up"; }
else { $cmd .= " down"; }
local $out = &backquote_logged("$cmd 2>&1");
if ($?) { &error("$cmd : $out"); }
if ($a->{'ether'}) {
	$out = &backquote_logged(
		"ifconfig $a->{'name'} ether $a->{'ether'} 2>&1");
	if ($? && $out !~ /Device busy/) { &error($out); }
	}
}

# deactivate_interface(&details)
# Deactive an interface
sub deactivate_interface
{
local $a = $_[0];
local $cmd;
if ($a->{'virtual'} eq "") {
	$cmd = "ifconfig $a->{'name'} unplumb";
	}
elsif ($gconfig{'os_version'} >= 8) {
	$cmd = "ifconfig $a->{'name'}:$a->{'virtual'} unplumb";
	}
else {
	$cmd = "ifconfig $a->{'name'}:$a->{'virtual'} 0.0.0.0 down";
	}
local $out = &backquote_logged("$cmd 2>&1");
if ($?) { &error($out); }
}

# boot_interfaces()
# Returns a list of interfaces brought up at boot time
sub boot_interfaces
{
local (@rv, $f, %mask);
push(@rv, { 'name' => 'lo0',
	    'fullname' => 'lo0',
	    'address' => '127.0.0.1',
	    'netmask' => '255.0.0.0',
	    'up' => 1,
	    'edit' => 0 });
open(MASK, "/etc/netmasks");
while(<MASK>) {
	s/\r|\n//g;
	s/#.*$//g;
	if (/([0-9\.]+)\s+([0-9\.]+)/) {
		$mask{$1} = $2;
		}
	}
close(MASK);
opendir(ETC, "/etc");
while($f = readdir(ETC)) {
	if ($f =~ /^hostname.(\S+):(\d+)$/ || $f =~ /^hostname.(\S+)/) {
		local %ifc;
		$ifc{'fullname'} = $ifc{'name'} = $1;
		$ifc{'virtual'} = $2 if (defined($2));
		$ifc{'fullname'} .= ":$2" if (defined($2));
		$ifc{'index'} = scalar(@rv);
		$ifc{'edit'}++;
		$ifc{'file'} = "/etc/$f";
		open(FILE, "/etc/$f");
		chop($ifc{'address'} = <FILE>);
		close(FILE);
		if ($ifc{'address'}) {
			&to_ipaddress($ifc{'address'})
				=~ /(\d+)\.(\d+)\.(\d+)\.(\d+)/;
			local ($a1, $a2, $a3, $a4) = ($1, $2, $3, $4);
			$ifc{'netmask'} = "255.255.255.0";
			local $netaddr;
			foreach $netaddr (keys %mask)
			{
				$mask{$netaddr} =~ /(\d+)\.(\d+)\.(\d+)\.(\d+)/;
				local $na = sprintf "%d.%d.%d.%d",
						int($a1) & int($1),
						int($a2) & int($2),
						int($a3) & int($3),
						int($a4) & int($4);
				$ifc{'netmask'} = $mask{$netaddr}  if ($na eq $netaddr);
			}
			$ifc{'netmask'} =~ /(\d+)\.(\d+)\.(\d+)\.(\d+)/;
			$ifc{'broadcast'} = sprintf "%d.%d.%d.%d",
						($a1 | ~int($1))&0xff,
						($a2 | ~int($2))&0xff,
						($a3 | ~int($3))&0xff,
						($a4 | ~int($4))&0xff;
			}
		else {
			$ifc{'dhcp'}++;
			}
		$ifc{'up'}++;
		push(@rv, \%ifc);
		}
	}
closedir(ETC);
return @rv;
}

# save_interface(&details)
# Create or update a boot-time interface
sub save_interface
{
local $name = $_[0]->{'virtual'} ne "" ? $_[0]->{'name'}.":".$_[0]->{'virtual'}
				       : $_[0]->{'name'};
&lock_file("/etc/hostname.$name");
open(IFACE, ">/etc/hostname.$name");
if (!$_[0]->{'dhcp'}) {
	print IFACE $_[0]->{'address'},"\n";
	}
close(IFACE);
&unlock_file("/etc/hostname.$name");
}

# delete_interface(&details)
# Delete a boot-time interface
sub delete_interface
{
local $name = $_[0]->{'virtual'} ne "" ? $_[0]->{'name'}.":".$_[0]->{'virtual'}
				       : $_[0]->{'name'};
&lock_file("/etc/hostname.$name");
unlink("/etc/hostname.$name");
&unlock_file("/etc/hostname.$name");
}

# iface_type(name)
# Returns a human-readable interface type name
sub iface_type
{
return "Fast Ethernet" if ($_[0] =~ /^hme/);
return "Loopback" if ($_[0] =~ /^lo/);
return "Token Ring" if ($_[0] =~ /^tr/);
return "PPP" if ($_[0] =~ /^ipdptp/ || $_[0] =~ /^ppp/);
return "Ethernet";
}

# iface_hardware(name)
# Does some interface have an editable hardware address
sub iface_hardware
{
return $_[0] !~ /^(lo|ipdptp|ppp)/;
}

# can_edit(what)
# Can some boot-time interface parameter be edited?
sub can_edit
{
return $_[0] eq "dhcp";
}

# valid_boot_address(address)
# Is some address valid for a bootup interface
sub valid_boot_address
{
return 1 if (&check_ipaddress($_[0]));
return gethostbyname($_[0]) ? 1 : 0;
}

# get_dns_config()
# Returns a hashtable containing keys nameserver, domain, search & order
sub get_dns_config
{
local $dns;
open(RESOLV, "/etc/resolv.conf");
while(<RESOLV>) {
	s/\r|\n//g;
	s/#.*$//g;
	if (/nameserver\s+(.*)/) {
		push(@{$dns->{'nameserver'}}, split(/\s+/, $1));
		}
	elsif (/domain\s+(\S+)/) {
		$dns->{'domain'} = [ $1 ];
		}
	elsif (/search\s+(.*)/) {
		$dns->{'domain'} = [ split(/\s+/, $1) ];
		}
	}
close(RESOLV);
open(SWITCH, "/etc/nsswitch.conf");
while(<SWITCH>) {
	s/\r|\n//g;
	if (/hosts:\s+(.*)/) {
		$dns->{'order'} = $1;
		}
	}
close(SWITCH);
$dns->{'files'} = [ "/etc/resolv.conf", "/etc/nsswitch.conf" ];
return $dns;
}

# save_dns_config(&config)
# Writes out the resolv.conf and nsswitch.conf files
sub save_dns_config
{
&lock_file("/etc/resolv.conf");
open(RESOLV, "/etc/resolv.conf");
local @resolv = <RESOLV>;
close(RESOLV);
open(RESOLV, ">/etc/resolv.conf");
foreach (@{$_[0]->{'nameserver'}}) {
	print RESOLV "nameserver $_\n";
	}
if ($_[0]->{'domain'}) {
	if ($_[0]->{'domain'}->[1]) {
		print RESOLV "search ",join(" ", @{$_[0]->{'domain'}}),"\n";
		}
	else {
		print RESOLV "domain $_[0]->{'domain'}->[0]\n";
		}
	}
foreach (@resolv) {
	print RESOLV $_ if (!/^\s*(nameserver|domain|search)\s+/);
	}
close(RESOLV);
&unlock_file("/etc/resolv.conf");

&lock_file("/etc/nsswitch.conf");
open(SWITCH, "/etc/nsswitch.conf");
local @switch = <SWITCH>;
close(SWITCH);
open(SWITCH, ">/etc/nsswitch.conf");
foreach (@switch) {
	if (/hosts:\s+/) {
		print SWITCH "hosts:\t$_[0]->{'order'}\n";
		}
	else { print SWITCH $_; }
	}
close(SWITCH);
&unlock_file("/etc/nsswitch.conf");
}

$max_dns_servers = 3;

# order_input(&dns)
# Returns HTML for selecting the name resolution order
sub order_input
{
if ($_[0]->{'order'} =~ /\[/) {
	# Using a complex resolve list
	return "<input name=order size=45 value=\"$_[0]->{'order'}\">\n";
	}
else {
	# Can select by menus
	local @o = split(/\s+/, $_[0]->{'order'});
	local ($rv, $i, $j);
	local @srcs = ( "", "files", "dns", "nis", "nisplus", "ldap" );
	local @srcn = ( "", "Hosts", "DNS", "NIS", "NIS+", "LDAP" );
	for($i=1; $i<@srcs; $i++) {
		local $ii = $i-1;
		$rv .= "<select name=order_$ii>\n";
		for($j=0; $j<@srcs; $j++) {
			$rv .= sprintf "<option value=\"%s\" %s>%s\n",
					$srcs[$j],
					$o[$ii] eq $srcs[$j] ? "selected" : "",
				        $srcn[$j] ? $srcn[$j] : "&nbsp;";
			}
		$rv .= "</select>\n";
		}
	return $rv;
	}
}

# parse_order(&dns)
# Parses the form created by order_input()
sub parse_order
{
if (defined($in{'order'})) {
	$in{'order'} =~ /\S/ || &error($text{'dns_eorder'});
	$_[0]->{'order'} = $in{'order'};
	}
else {
	local($i, @order);
	for($i=0; defined($in{"order_$i"}); $i++) {
		push(@order, $in{"order_$i"}) if ($in{"order_$i"});
		}
	$_[0]->{'order'} = join(" ", @order);
	}
}

# get_hostname()
sub get_hostname
{
return &get_system_hostname();
}

# save_hostname(name)
sub save_hostname
{
&system_logged("hostname $_[0] >/dev/null 2>&1");
}

# get_domainname()
sub get_domainname
{
local $d = `domainname`;
chop($d);
return $d;
}

# save_domainname(domain)
sub save_domainname
{
system("domainname \"$_[0]\" >/dev/null 2>&1");
if ($_[0]) {
	open(DOMAIN, ">/etc/defaultdomain");
	print DOMAIN $_[0],"\n";
	close(DOMAIN);
	}
else { unlink("/etc/defaultdomain"); }
}

sub routing_config_files
{
return ( "/etc/defaultrouter", "/etc/notrouter", "/etc/gateways" );
}

sub routing_input
{
# show default router(s) input
local(@defrt);
open(DEFRT, "/etc/defaultrouter");
while(<DEFRT>) {
	s/#.*$//g;
	if (/(\S+)/) { push(@defrt, $1); }
	}
close(DEFRT);
print "<tr> <td valign=top><b>$text{'routes_defaults'}</b></td>\n";
print "<td><textarea name=defrt rows=3 cols=40>",
	join("\n", @defrt),"</textarea></td> </tr>\n";

# show router input
local $notrt = (-r "/etc/notrouter");
local $gatew = (-r "/etc/gateways");
print "<tr> <td><b>Act as router?</b></td> <td>\n";
printf "<input type=radio name=router value=0 %s> $text{'yes'}\n",
	$gatew && !$notrt ? "checked" : "";
printf "<input type=radio name=router value=1 %s> $text{'routes_possible'}\n",
	!$gatew && !$notrt ? "checked" : "";
printf "<input type=radio name=router value=2 %s> $text{'no'}\n",
	$notrt ? "checked" : "";
print "</td> </tr>\n";
}

sub parse_routing
{
local @defrt = split(/\s+/, $in{'defrt'});
foreach $d (@defrt) {
	gethostbyname($d) || &error(&text('routes_edefault', $d));
	}
&lock_file("/etc/defaultrouter");
if (@defrt) {
	open(DEFRT, ">/etc/defaultrouter");
	foreach $d (@defrt) { print DEFRT $d,"\n"; }
	close(DEFRT);
	}
else { unlink("/etc/defaultrouter"); }
&unlock_file("/etc/defaultrouter");

&lock_file("/etc/gateways");
&lock_file("/etc/notrouter");
if ($in{'router'} == 0) {
	&create_empty_file("/etc/gateways");
	unlink("/etc/notrouter");
	}
elsif ($in{'router'} == 2) {
	&create_empty_file("/etc/notrouter");
	unlink("/etc/gateways");
	}
else {
	unlink("/etc/gateways");
	unlink("/etc/notrouter");
	}
&unlock_file("/etc/gateways");
&unlock_file("/etc/notrouter");
}

# create_empty_file(filename)
sub create_empty_file
{
if (!-r $_[0]) {
	open(EMPTY,">$_[0]");
	close(EMPTY);
	}
}

sub os_feedback_files
{
opendir(DIR, "/etc");
local @f = map { "/etc/$_" } grep { /^hostname\./ } readdir(DIR);
closedir(DIR);
return ( @f, "/etc/netmasks", "/etc/resolv.conf", "/etc/nsswitch.conf",
	 "/etc/defaultrouter", "/etc/notrouter", "/etc/gateways" );
}

1;

