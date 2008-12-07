#!/usr/bin/perl
# setup.cgi
# Setup an initial save file

require './firewall-lib.pl';
&ReadParse();
$access{'setup'} || &error($text{'setup_ecannot'});

&lock_file($iptables_save_file);
if ($in{'reset'}) {
	# Clear out all rules
	foreach $t ("filter", "nat", "mangle") {
		&system_logged("iptables -t $t -P INPUT ACCEPT >/dev/null 2>&1");
		&system_logged("iptables -t $t -P OUTPUT ACCEPT >/dev/null 2>&1");
		&system_logged("iptables -t $t -P FORWARD ACCEPT >/dev/null 2>&1");
		&system_logged("iptables -t $t -P PREROUTING ACCEPT >/dev/null 2>&1");
		&system_logged("iptables -t $t -P POSTROUTING ACCEPT >/dev/null 2>&1");
		&system_logged("iptables -t $t -F >/dev/null 2>&1");
		&system_logged("iptables -t $t -X >/dev/null 2>&1");
		}
	}

# Save all existing active rules
if (defined(&unapply_iptables)) {
	&unapply_iptables();
	}
else {
	&backquote_logged("iptables-save >$iptables_save_file 2>&1");
	}

if ($in{'auto'}) {
	@tables = &get_iptables_save();
	if ($in{'auto'} == 1) {
		# Add a single rule to the nat table for masquerading
		$iface = $in{'iface1'} || $in{'iface1_other'};
		$iface || &error($text{'setup_eiface'});
		($table) = grep { $_->{'name'} eq 'nat' } @tables;
		push(@{$table->{'rules'}},
		     	{ 'chain' => 'POSTROUTING',
			  'o' => [ "", $iface ],
			  'j' => [ "", 'MASQUERADE' ] } );
		}
	elsif ($in{'auto'} >= 2) {
		# Block all incoming traffic, except for established
		# connections, DNS replies and safe ICMP types
		# In mode 3 allow ssh and ident too
		# In mode 4 allow ftp, echo-request and high ports too
		$iface = $in{'iface'.$in{'auto'}} ||
			 $in{'iface'.$in{'auto'}.'_other'};
		$iface || &error($text{'setup_eiface'});
		($table) = grep { $_->{'name'} eq 'filter' } @tables;
		$table->{'defaults'}->{'INPUT'} = 'DROP';
		push(@{$table->{'rules'}},
		     { 'chain' => 'INPUT',
		       'i' => [ "!", $iface ],
		       'j' => [ "", 'ACCEPT' ],
		       'cmt' => 'Accept traffic from internal interfaces' },
		     { 'chain' => 'INPUT',
		       'm' => [ [ "", "tcp" ] ],
		       'p' => [ "", "tcp" ],
		       'tcp-flags' => [ "", "ACK", "ACK" ],
		       'j' => [ "", 'ACCEPT' ],
		       'cmt' => 'Accept traffic with the ACK flag set' },
		     { 'chain' => 'INPUT',
		       'm' => [ [ "", "state" ] ],
		       'state' => [ "", "ESTABLISHED" ],
		       'j' => [ "", 'ACCEPT' ],
		       'cmt' => 'Allow incoming data that is part of a connection we established' },
		     { 'chain' => 'INPUT',
		       'm' => [ [ "", "state" ] ],
		       'state' => [ "", "RELATED" ],
		       'j' => [ "", 'ACCEPT' ],
		       'cmt' => 'Allow data that is related to existing connections' },
		     { 'chain' => 'INPUT',
		       'm' => [ [ "", "udp" ] ],
		       'p' => [ "", "udp" ],
		       'sport' => [ "", 53 ],
		       'dport' => [ "", "1024:65535" ],
		       'j' => [ "", 'ACCEPT' ],
		       'cmt' => 'Accept responses to DNS queries' },
		     { 'chain' => 'INPUT',
		       'm' => [ [ "", "icmp" ] ],
		       'p' => [ [ "", "icmp" ] ],
		       'icmp-type' => [ "", "echo-reply" ],
		       'j' => [ "", 'ACCEPT' ],
		       'cmt' => 'Accept responses to our pings' },
		     { 'chain' => 'INPUT',
		       'm' => [ [ "", "icmp" ] ],
		       'p' => [ [ "", "icmp" ] ],
		       'icmp-type' => [ "", "destination-unreachable" ],
		       'j' => [ "", 'ACCEPT' ],
		       'cmt' => 'Accept notifications of unreachable hosts' },
		     { 'chain' => 'INPUT',
		       'm' => [ [ "", "icmp" ] ],
		       'p' => [ [ "", "icmp" ] ],
		       'icmp-type' => [ "", "source-quench" ],
		       'j' => [ "", 'ACCEPT' ],
		       'cmt' => 'Accept notifications to reduce sending speed' },
		     { 'chain' => 'INPUT',
		       'm' => [ [ "", "icmp" ] ],
		       'p' => [ [ "", "icmp" ] ],
		       'icmp-type' => [ "", "time-exceeded" ],
		       'j' => [ "", 'ACCEPT' ],
		       'cmt' => 'Accept notifications of lost packets' },
		     { 'chain' => 'INPUT',
		       'm' => [ [ "", "icmp" ] ],
		       'p' => [ [ "", "icmp" ] ],
		       'icmp-type' => [ "", "parameter-problem" ],
		       'j' => [ "", 'ACCEPT' ],
		       'cmt' => 'Accept notifications of protocol problems' }
			);
		if ($in{'auto'} >= 3) {
			# Allow ssh and ident
			push(@{$table->{'rules'}},
			     { 'chain' => 'INPUT',
			       'm' => [ [ "", "tcp" ] ],
			       'p' => [ "", "tcp" ],
			       'dport' => [ "", "ssh" ],
			       'j' => [ "", 'ACCEPT' ],
			       'cmt' => 'Allow connections to our SSH server' },
			     { 'chain' => 'INPUT',
			       'm' => [ [ "", "tcp" ] ],
			       'p' => [ "", "tcp" ],
			       'dport' => [ "", "auth" ],
			       'j' => [ "", 'ACCEPT' ],
			       'cmt' => 'Allow connections to our IDENT server'}
				);
			}
		if ($in{'auto'} == 4) {
			# Allow pings and most high ports
			push(@{$table->{'rules'}},
			     { 'chain' => 'INPUT',
			       'm' => [ [ "", "icmp" ] ],
			       'p' => [ [ "", "icmp" ] ],
			       'icmp-type' => [ "", "echo-request" ],
			       'j' => [ "", 'ACCEPT' ],
			       'cmt' => 'Respond to pings' },
			     { 'chain' => 'INPUT',
			       'm' => [ [ "", "tcp" ] ],
			       'p' => [ "", "tcp" ],
			       'dport' => [ "", "2049:2050" ],
			       'j' => [ "", 'DROP' ],
			       'cmt' => 'Protect our NFS server' },
			     { 'chain' => 'INPUT',
			       'm' => [ [ "", "tcp" ] ],
			       'p' => [ "", "tcp" ],
			       'dport' => [ "", "6000:6063" ],
			       'j' => [ "", 'DROP' ],
			       'cmt' => 'Protect our X11 display server' },
			     { 'chain' => 'INPUT',
			       'm' => [ [ "", "tcp" ] ],
			       'p' => [ "", "tcp" ],
			       'dport' => [ "", "7000:7010" ],
			       'j' => [ "", 'DROP' ],
			       'cmt' => 'Protect our X font server' },
			     { 'chain' => 'INPUT',
			       'm' => [ [ "", "tcp" ] ],
			       'p' => [ "", "tcp" ],
			       'dport' => [ "", "1024:65535" ],
			       'j' => [ "", 'ACCEPT' ],
			       'cmt' => 'Allow connections to unprivileged ports' },
				);
			}
		}
	&run_before_command();
	&save_table($table);
	&run_after_command();
	&copy_to_cluster();
	}

if ($in{'atboot'}) {
	&create_firewall_init();
	}
&unlock_file($iptables_save_file);

&webmin_log("setup");
&redirect("");


