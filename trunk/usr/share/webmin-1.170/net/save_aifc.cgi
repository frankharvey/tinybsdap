#!/usr/bin/perl
# save_aifc.cgi
# Save, create or delete an active interface

require './net-lib.pl';
&ReadParse();
@acts = &active_interfaces();

if ($in{'delete'}) {
	# delete an interface
	&error_setup($text{'aifc_err1'});
	$a = $acts[$in{'idx'}];
	&can_iface($a) || &error($text{'ifcs_ecannot_this'});
	&deactivate_interface($a);
	&webmin_log("delete", "aifc", $a->{'fullname'}, $a);
	}
else {
	# Validate and save inputs
	&error_setup($text{'aifc_err2'});
	if (!$in{'new'}) {
		$olda = $acts[$in{'idx'}];
		&can_iface($olda) || &error($text{'ifcs_ecannot_this'});
		$a->{'name'} = $olda->{'name'};
		$a->{'virtual'} = $olda->{'virtual'}
			if (defined($olda->{'virtual'}));
		}
	elsif (defined($in{'virtual'})) {
		# creating a virtual interface
		$in{'virtual'} =~ /^\d+$/ ||
			&error($text{'aifc_evirt'});
		$in{'virtual'} >= $min_virtual_number ||
			&error(&text('aifc_evirtmin', $min_virtual_number));
		foreach $ea (@acts) {
			if ($ea->{'name'} eq $in{'name'} &&
			    $ea->{'virtual'} eq $in{'virtual'}) {
				&error(&text('aifc_evirtdup',
				       "$in{'name'}:$in{'virtual'}"));
				}
			}
		$a->{'name'} = $in{'name'};
		$a->{'virtual'} = $in{'virtual'};
		&can_create_iface() || &error($text{'ifcs_ecannot'});
		&can_iface($a) || &error($text{'ifcs_ecannot'});
		}
	elsif ($in{'name'} =~ /^([a-z]+\d*(\.\d+)?):(\d+)$/) {
		# also creating a virtual interface
		foreach $ea (@acts) {
			if ($ea->{'name'} eq $1 &&
			    $ea->{'virtual'} eq $3) {
				&error(&text('aifc_evirtdup', $in{'name'}));
				}
			}
		$3 >= $min_virtual_number ||
			&error(&text('aifc_evirtmin', $min_virtual_number));
		$a->{'name'} = $1;
		$a->{'virtual'} = $3;
		&can_create_iface() || &error($text{'ifcs_ecannot'});
		&can_iface($a) || &error($text{'ifcs_ecannot'});
		}
	elsif ($in{'name'} =~ /^[a-z]+\d*(\.\d+)?$/) {
		# creating a real interface
		foreach $ea (@acts) {
			if ($ea->{'name'} eq $in{'name'}) {
				&error(&text('aifc_edup', $in{'name'}));
				}
			}
		$a->{'name'} = $in{'name'};
		&can_create_iface() || &error($text{'ifcs_ecannot'});
		&can_iface($a) || &error($text{'ifcs_ecannot'});
		}
	else {
		&error($text{'aifc_ename'});
		}

	# Check for address clash
	$allow_clash = defined(&allow_interface_clash) ?
			&allow_interface_clash($a, 0) : 1;
	if (!$allow_clash &&
	    ($in{'new'} || $olda->{'address'} ne $a->{'address'})) {
		($clash) = grep { $_->{'address'} eq $a->{'address'} } @acts;
		$clash && &error(&text('aifc_eclash', $clash->{'fullname'}));
		}

	# Validate and store inputs
	&check_ipaddress($in{'address'}) ||
		&error(&text('aifc_eip', $in{'address'}));
	$a->{'address'} = $in{'address'};
	if (!$in{'netmask_def'}) {
		&check_ipaddress($in{'netmask'}) ||
			&error(&text('aifc_emask', $in{'netmask'}));
		$a->{'netmask'} = $in{'netmask'};
		}
	elsif ($virtual_netmask && $a->{'virtual'} ne "") {
		$a->{'netmask'} = $virtual_netmask;
		}
	if (!$in{'broadcast_def'}) {
		&check_ipaddress($in{'broadcast'}) ||
			&error(&text('aifc_ebroad', $in{'broadcast'}));
		$a->{'broadcast'} = $in{'broadcast'};
		}
	if (!$in{'mtu_def'}) {
		$in{'mtu'} =~ /^\d+$/ ||
			&error(&text('aifc_emtu', $in{'mtu'}));
		$a->{'mtu'} = $in{'mtu'} if ($olda->{'mtu'} ne $in{'mtu'});
		}
	if ($in{'up'}) { $a->{'up'}++; }
	if (!$in{'ether_def'} && $a->{'virtual'} eq "" &&
	    &iface_hardware($a->{'name'})) {
		$in{'ether'} =~ /^[A-Fa-f0-9:]+$/ ||
			&error(&text('aifc_ehard', $in{'ether'}));
		$a->{'ether'} = $in{'ether'}
			if ($olda->{'ether'} ne $in{'ether'});
		}
	$a->{'fullname'} = $a->{'name'}.
			   ($a->{'virtual'} eq '' ? '' : ':'.$a->{'virtual'});

	# Bring it up
	&activate_interface($a);
	&webmin_log($in{'new'} ? 'create' : 'modify',
		    "aifc", $a->{'fullname'}, $a);
	}
&redirect("list_ifcs.cgi");

