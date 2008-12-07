#!/usr/bin/perl
# list_leases.cgi
# List all active leases

require './dhcpd-lib.pl';
require 'timelocal.pl';
&ReadParse();
$timenow = time();

%access = &get_module_acl();
&error_setup("<blink><font color=red>$text{'eacl_aviol'}</font></blink>");
&error("$text{'eacl_np'} $text{'eacl_psl'}") unless $access{'r_leases'};

if ($in{'network'}) {
	$desc = &text('listl_network', "<tt>$in{'network'}</tt>",
			       "<tt>$in{'netmask'}</tt>");
	}
&ui_print_header($desc, $text{'listl_header'}, "");

if (!-r $config{'lease_file'}) {
	print "<b>";
	print(&text('listl_lfnotexist',$config{'lease_file'}));
	print "</b><p>\n";
	}
elsif (!&tokenize_file($config{'lease_file'}, \@tok)) {
	print "<b>",&text('listl_lfnotcont',$config{'lease_file'}),"</b><p>\n";
	}
else {
	$i = $j = 0;
	local @nw = split(/\./, $in{'network'});
	local @nm = split(/\./, $in{'netmask'});
	LEASE: while($i < @tok) {
		$lease = &parse_struct(\@tok, \$i, $j++, $config{'lease_file'});
		next if (!$lease);
		local $mems = $lease->{'members'};
		local $starts = &find('starts', $mems);
		local $ends = &find('ends', $mems);
		$lease->{'stime'} = &lease_time($starts);
		$lease->{'etime'} = &lease_time($ends);
		if ($lease->{'etime'} < $timenow ||
		    $lease->{'stime'} > $timenow) {
			if ($in{'all'}) { $lease->{'expired'}++; }
			else { next; }
			}
		if ($in{'network'}) {
			# Is lease within network/netmask?
			local @ad = split(/\./, $lease->{'values'}->[0]);
			for($k=0; $k<4; $k++) {
				if ((int($ad[$k]) & int($nm[$k])) !=
				    int($nw[$k])) {
					next LEASE;
					}
				}
			}
		push(@leases, $lease);
		}
	if (@leases) {
		if ($in{'sort'} eq 'ipaddr') {
			@leases = sort { &ip_compare($a, $b) } @leases;
			}
		elsif ($in{'sort'} eq 'ether') {
			@leases = sort { &ether_compare($a, $b) } @leases;
			}
		elsif ($in{'sort'} eq 'host') {
			@leases = sort { &hostname_compare($a, $b) } @leases;
			}
		elsif ($in{'sort'} eq 'start') {
			@leases = sort { $a->{'stime'} <=> $b->{'stime'} } @leases;
			}
		elsif ($config{'lease_sort'} == 1) {
			@leases = sort { &ip_compare($a, $b) } @leases;
			}
		elsif ($config{'lease_sort'} == 2) {
			@leases = sort { &hostname_compare($a, $b) } @leases;
			}
		print "<table border width=100%>\n";
		$sl = "<a href=list_leases.cgi?all=$in{'all'}&network=$in{'network'}&netmask=$in{'netmask'}&sort=";
		print "<tr $tb> ",
		      "<td>${sl}ipaddr><b>$text{'listl_ipaddr'}</b></a></td> ",
		      "<td>${sl}ether><b>$text{'listl_ether'}</b></a></td> ",
		      "<td>${sl}host><b>$text{'listl_host'}</b></a></td> ",
		      "<td>${sl}start><b>$text{'listl_start'}</b></a></td> ",
		      "<td>$text{'listl_end'}</b></td> </tr>\n";
		foreach $lease (@leases) {
			local $mems = $lease->{'members'};
			local $starts = &find('starts', $mems);
			local $ends = &find('ends', $mems);
			print "<tr $cb>\n";
			local $ht = $lease->{'expired'} ? "i" : "tt";
			print "<td><$ht><a href='delete_lease.cgi?",
			      "idx=$lease->{'index'}&all=$in{all}&",
			      "network=$in{'network'}&netmask=$in{'netmask'}'>",
			      "$lease->{'values'}->[0]</a></$ht></td>\n";
			local $hard = &find('hardware', $mems);
			print "<td><tt>",$hard->{'values'}->[1],"</tt></td>\n";
			local $client = &find('client-hostname', $mems);
			print "<td><tt>",$client ?
				&html_escape($client->{'values'}->[0]) :
				"<br>","</tt></td>\n";
			if ($config{'lease_tz'}) {
				local @st = localtime($lease->{'stime'});
				local @et = localtime($lease->{'etime'});
				$s = sprintf "%4.4d/%2.2d/%2.2d %2.2d:%2.2d:%2.2d", $st[5]+1900, $st[4]+1, $st[3], $st[2], $st[1], $st[0];
				$e = sprintf "%4.4d/%2.2d/%2.2d %2.2d:%2.2d:%2.2d", $et[5]+1900, $et[4]+1, $et[3], $et[2], $et[1], $et[0];
				}
			else {
				$s = $starts->{'values'}->[1]." ".
				     $starts->{'values'}->[2];
				$e = $ends->{'values'}->[1]." ".
				     $ends->{'values'}->[2];
				}

			print "<td><tt>$s</tt></td>\n";
			print "<td><tt>$e</tt></td>\n";
			print "</tr>\n";
			}
		print "</table>$text{'listl_delete'}<p>\n";
		}
	else {
		print "<b>",&text($in{'all'} ? 'listl_lfnotcont' :
				  'listl_lfnotcont2', $config{'lease_file'}),
		      "</b><p>\n";
		}
	if (!$in{'all'}) {
		print "<form action=list_leases.cgi>\n";
		print "<input type=hidden name=all value=1>\n";
		print "<input type=hidden name=network value='$in{'network'}'>\n";
		print "<input type=hidden name=netmask value='$in{'netmask'}'>\n";
		print "<input type=submit value='$text{'listl_all'}'>\n";
		print "</form>\n";
		}
	}

&ui_print_footer("", $text{'listl_return'});

sub lease_time
{
local @d = split(/\//, $_[0]->{'values'}->[1]);
local @t = split(/:/, $_[0]->{'values'}->[2]);
local $t;
eval { $t = timegm($t[2], $t[1], $t[0], $d[2], $d[1]-1, $d[0]-1900) };
return $@ ? undef : $t;
}

sub ip_compare
{
$a->{'values'}->[0] =~ /^(\d+)\.(\d+)\.(\d+)\.(\d+)/;
local ($a1, $a2, $a3, $a4) = ($1, $2, $3, $4);
$b->{'values'}->[0] =~ /^(\d+)\.(\d+)\.(\d+)\.(\d+)/;
return	$a1 < $1 ? -1 :
	$a1 > $1 ? 1 :
	$a2 < $2 ? -1 :
	$a2 > $2 ? 1 :
	$a3 < $3 ? -1 :
	$a3 > $3 ? 1 :
	$a4 < $4 ? -1 :
	$a4 > $4 ? 1 : 0;
}

sub hostname_compare
{
local $client_a = &find_value('client-hostname', $a->{'members'});
local $client_b = &find_value('client-hostname', $b->{'members'});
return lc($client_a) cmp lc($client_b);
}

sub ether_compare
{
local $ether_a = &find('hardware', $a->{'members'});
local $ether_b = &find('hardware', $b->{'members'});
return lc($ether_a->{'values'}->[1]) cmp lc($ether_b->{'values'}->[1]);
}

