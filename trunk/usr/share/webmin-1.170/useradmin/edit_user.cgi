#!/usr/local/bin/perl
# edit_user.cgi
# Display a form for editing a user, or creating a new user

require './user-lib.pl';
require 'timelocal.pl';
&ReadParse();
$n = $in{'num'};
%access = &get_module_acl();
if ($n eq "") {
	$access{'ucreate'} || &error($text{'uedit_ecreate'});
	&ui_print_header(undef, $text{'uedit_title2'}, "", "create_user");
	}
else {
	@ulist = &list_users();
	%uinfo = %{$ulist[$n]};
	&can_edit_user(\%access, \%uinfo) || &error($text{'uedit_eedit'});
	&ui_print_header(undef, $text{'uedit_title'}, "", "edit_user");
	}

# build list of used shells
@shlist = ($config{'default_shell'} ? ( $config{'default_shell'} ) : ( ),
	   "/bin/sh", "/bin/csh", "/bin/false");
&build_user_used(\%used, \@shlist);
open(SHELLS, "/etc/shells");
while(<SHELLS>) {
	s/\r|\n//g;
	s/#.*$//;
	push(@shlist, $_) if (/\S/);
	}
close(SHELLS);

print "<form action=save_user.cgi method=post>\n";
if ($n ne "") {
	print "<input type=hidden name=num value=\"$n\">\n";
	}
print "<table border width=100%>\n";
print "<tr $tb> <td><b>$text{'uedit_details'}</b></td> </tr>\n";
print "<tr $cb> <td><table width=100%>\n";

print "<tr> <td>",&hlink("<b>$text{'user'}</b>","user"),"</td>\n";
if ($n eq "" && $config{'new_user_group'} && $access{'gcreate'}) {
	$onch = "newgid.value = user.value";
	}
print "<td><input name=user size=10 value=\"$uinfo{'user'}\" onChange='$onch'></td>\n";

print "<td>",&hlink("<b>$text{'uid'}</b>","uid"),"</td>\n";
if ($n eq "") {
    $defuid = &allocate_uid(\%used);
    print "<td>\n";

    if ( $access{'calcuid'} && $access{'autouid'} && $access{'useruid'} ) {
        # Show options for calculated, auto-incremented and user entered UID
        printf "<input type=radio name=uid_def value=1 %s> %s\n",
            $config{'uid_mode'} eq '1' ? "checked" : "",
            $text{'uedit_uid_def'};
        printf "<input type=radio name=uid_def value=2 %s> %s\n",
            $config{'uid_mode'} eq '2' ? "checked" : "",
            $text{'uedit_uid_calc'};
        printf "<input type=radio name=uid_def value=0 %s> %s\n",
            $config{'uid_mode'} eq '0' ? "checked" : "",
	    "<input name=uid size=10 value='$defuid'>";
    }

    if ( $access{'calcuid'} && $access{'autouid'} && !$access{'useruid'} ) {
	# Show options for calculated and auto-incremented UID
        printf "<input type=radio name=uid_def value=1 %s> %s\n",
            $config{'uid_mode'} eq '1' ? "checked" : "",
            $text{'uedit_uid_def'};
        printf "<input type=radio name=uid_def value=2 %s> %s\n",
            $config{'uid_mode'} eq '2' ? "checked" : "",
            $text{'uedit_uid_calc'};
    }

    if ( $access{'calcuid'} && !$access{'autouid'} && $access{'useruid'} ) {
	# Show options for calculated and user entered UID
        printf "<input type=radio name=uid_def value=2 %s> %s\n",
            $config{'uid_mode'} eq '2' ? "checked" : "",
            $text{'uedit_uid_calc'};
        printf "<input type=radio name=uid_def value=0 %s> %s\n",
            $config{'uid_mode'} eq '0' ? "checked" : "",
	    "<input name=uid size=10 value='$defuid'>";
    }

    if ( !$access{'calcuid'} && $access{'autouid'} && $access{'useruid'} ) {
        # Show options for auto-incremented and user entered UID
        printf "<input type=radio name=uid_def value=1 %s> %s\n",
            $config{'uid_mode'} eq '1' ? "checked" : "",
            $text{'uedit_uid_def'};
        printf "<input type=radio name=uid_def value=0 %s> %s\n",
            $config{'uid_mode'} eq '0' ? "checked" : "",
	    "<input name=uid size=10 value='$defuid'>";
    }

    if ( $access{'calcuid'} && !$access{'autouid'} && !$access{'useruid'} ) {
        # Hidden field  for calculated UID
	print "<input type=hidden name=uid_def value=2>";
	print "$text{'uedit_uid_calc'}\n";
    }

    if ( !$access{'calcuid'} && $access{'autouid'} && !$access{'useruid'} ) {
        # Hidden field for auto-incremented UID
	print "<input type=hidden name=uid_def value=1>";
	print "$text{'uedit_uid_calc'}\n";
    }

    if ( !$access{'calcuid'} && !$access{'autouid'} && $access{'useruid'} ) {
        # Show field for user entered UID
	print "<input type=hidden name=uid_def value=0>";
	print "UID: <input name=uid size=10 value='$defuid'>\n";
    }

    if ( !$access{'calcuid'} && !$access{'autouid'} && !$access{'useruid'} ) {
        if ( $config{'uid_mode'} eq '0' ) {
          print "<input type=hidden name=uid_def value=0>";
          print "UID: <input name=uid size=10 value='$defuid'>\n";
        } else {
          print "<input type=hidden name=uid_def value=$config{'uid_mode'}>";
          print "$text{'uedit_uid_def'}\n" if ( $config{'uid_mode'} eq '1' );
          print "$text{'uedit_uid_calc'}\n" if ( $config{'uid_mode'} eq '2' );
        }
    }
    print "</td></tr>\n";
    }
else {
	print "<td><input name=uid size=10 value='$uinfo{'uid'}'></td> </tr>\n";
	}

if ($config{'extra_real'}) {
	local @real = split(/,/, $uinfo{'real'}, 5);
	print "<tr> <td>",&hlink("<b>$text{'real'}</b>","real"),"</td>\n";
	print "<td><input name=real size=20 value=\"$real[0]\"></td>\n";

	print "<td>",&hlink("<b>$text{'office'}</b>","office"),"</td>\n";
	print "<td><input name=office size=20 value=\"$real[1]\"></td> </tr>\n";

	print "<tr> <td>",&hlink("<b>$text{'workph'}</b>","workph"),"</td>\n";
	print "<td><input name=workph size=20 value=\"$real[2]\"></td>\n";

	print "<td>",&hlink("<b>$text{'homeph'}</b>","homeph"),"</td>\n";
	print "<td><input name=homeph size=20 value=\"$real[3]\"></td> </tr>\n";

	print "<tr> <td>",&hlink("<b>$text{'extra'}</b>","extra"),"</td>\n";
	print "<td><input name=extra size=20 value=\"$real[4]\"></td>\n";
	}
else {
	print "<tr> <td>",&hlink("<b>$text{'real'}</b>","real"),"</td>\n";
	print "<td><input name=real size=20 value=\"$uinfo{'real'}\"></td>\n";
	}

print "<td>",&hlink("<b>$text{'home'}</b>","home"),"</td>\n";
if ($access{'autohome'}) {
	print "<td>$text{'uedit_auto'} ",
	      $n eq "" ? "" : "( <tt>$uinfo{'home'}</tt> )",
	      "</td>\n";
	}
else {
	print "<td>\n";
	if ($config{'home_base'}) {
		local $grp = &my_getgrgid($uinfo{'gid'});
		local $hb = $n eq "" || &auto_home_dir($config{'home_base'},
			    $uinfo{'user'}, $grp) eq $uinfo{'home'};
		printf "<input type=radio name=home_base value=1 %s> %s\n",
			$hb ? "checked" : "", $text{'uedit_auto'};
		printf "<input type=radio name=home_base value=0 %s>\n",
			$hb ? "" : "checked";
		printf "<input name=home size=25 value=\"%s\"> %s\n",
			$hb ? "" : $uinfo{'home'},
			&file_chooser_button("home", 1);
		}
	else {
		print "<input name=home size=25 value=\"$uinfo{'home'}\">\n",
		      &file_chooser_button("home", 1);
		}
	}
print "</td> </tr>\n";

print "<tr> <td valign=top>",&hlink("<b>$text{'shell'}</b>","shell"),"</td>\n";
print "<td valign=top><select name=shell>\n";
if ($access{'shells'} ne "*") {
	@shlist = %uinfo ? ($uinfo{'shell'}) : ();
	push(@shlist, split(/\s+/, $access{'shells'}));
	$shells = 1;
	}
$shells = 1 if ($access{'noother'});
@shlist = &unique(@shlist);
foreach $s (@shlist) {
	printf "<option value='%s' %s>%s\n", $s,
		$s eq $uinfo{'shell'} ? "selected" : "",
		$s eq "" ? "&lt;None&gt;" : $s;
	}
print "<option value=*>$text{'uedit_other'}\n" if (!$shells);
print "</select></td>\n";

$pass = %uinfo ? $uinfo{'pass'} : $config{'lock_string'};
if (!%uinfo && $config{'random_password'}) {
	&seed_random();
	foreach (1 .. 15) {
		$random_password .= $random_password_chars[
					rand(scalar(@random_password_chars))];
		}
	}
print "<td valign=top rowspan=4>",&hlink("<b>$text{'pass'}</b>","pass"),
      "</td> <td rowspan=4 valign=top>\n";
printf"<input type=radio name=passmode value=0 %s> %s<br>\n",
	$pass eq "" && $random_password eq "" ? "checked" : "",
	$config{'empty_mode'} ? $text{'none1'} : $text{'none2'};
printf"<input type=radio name=passmode value=1 %s> $text{'nologin'}<br>\n",
	$pass eq $config{'lock_string'} && $random_password eq "" ? "checked" : "";
printf "<input type=radio name=passmode value=3 %s> $text{'clear'}\n",
	$random_password ne "" ? "checked" : "";
printf "<input %s name=pass size=15 value='%s'><br>\n",
	$config{'passwd_stars'} ? "type=password" : "",
	$config{'random_password'} && $n eq "" ? $random_password : "";
if ($access{'nocrypt'}) {
	printf
	  "<input type=radio name=passmode value=2 %s> $text{'nochange'}\n",
	  $pass && $pass ne $config{'lock_string'} && $random_password eq "" ? "checked" : "";
	print "<input type=hidden name=encpass size=13 value=\"$pass\">\n";
	}
else {
	printf
	  "<input type=radio name=passmode value=2 %s> $text{'encrypted'}\n",
	  $pass && $pass ne $config{'lock_string'} ? "checked" : "";
	printf "<input name=encpass size=13 value=\"%s\">\n",
		$pass && $pass ne $config{'lock_string'} ? $pass : "";
	}
print "</td> </tr>\n";

if (!$shells) {
	print "<tr> <td valign=top>$text{'uedit_other'}</td>\n";
	print "<td valign=top><input size=25 name=othersh>\n";
	print &file_chooser_button("othersh", 0),"</td> </tr>\n";
	print "<tr> <td colspan=2><br></td> </tr>\n";
	}
print "</table></td></tr></table><p>\n";

$pft = &passfiles_type();
if (($pft == 1 || $pft == 6) && $access{'peopt'}) {
	# This is a BSD system.. a few extra password options are supported
	print "<table border width=100%>\n";
	print "<tr $tb> <td><b>$text{'uedit_passopts'}</b></td> </tr>\n";
	print "<tr $cb> <td><table width=100%>\n";
	print "<tr> <td>",&hlink("<b>$text{'change2'}</b>",
				 "change2"),"</td>\n";
	if ($uinfo{'change'}) {
		@tm = localtime($uinfo{'change'});
		$cday = $tm[3];
		$cmon = $tm[4]+1;
		$cyear = $tm[5]+1900;
		$chour = sprintf "%2.2d", $tm[2];
		$cmin = sprintf "%2.2d", $tm[1];
		}
	print "<td>";
	&date_input($cday, $cmon, $cyear, 'change');
	print " &nbsp; <input name=changeh size=3 value=\"$chour\">";
	print ":<input name=changemi size=3 value=\"$cmin\"></td>\n";

	print "<td>",&hlink("<b>$text{'expire2'}</b>","expire2"),"</td>\n";
	if ($uinfo{'expire'}) {
		@tm = localtime($uinfo{'expire'});
		$eday = $tm[3];
		$emon = $tm[4]+1;
		$eyear = $tm[5]+1900;
		$ehour = sprintf "%2.2d", $tm[2];
		$emin = sprintf "%2.2d", $tm[1];
		}
	print "<td>";
	&date_input($eday, $emon, $eyear, 'expire');
	print " &nbsp; <input name=expireh size=3 value=\"$ehour\">";
	print ":<input name=expiremi size=3 value=\"$emin\"></td> </tr>\n";

	print "<tr> <td>",&hlink("<b>$text{'class'}</b>","class"),"</td>\n";
	print "<td><input name=class size=10 value=\"$uinfo{'class'}\"></td>\n";
	print "</tr>\n";
	print "</table></td></tr></table><p>\n";
	}
elsif (($pft == 2 || $pft == 5) && $access{'peopt'}) {
	# System has a shadow password file as well.. which means it supports
	# password expiry and so on
	print "<table border width=100%>\n";
	print "<tr $tb> <td><b>$text{'uedit_passopts'}</b></td> </tr>\n";
	print "<tr $cb> <td><table width=100%>\n";
	print "<tr> <td>",&hlink("<b>$text{'change'}</b>","change"),"</td>\n";
	print "<td>";
	if ($uinfo{'change'}) {
		@tm = localtime(timelocal(gmtime($uinfo{'change'} * 60*60*24)));
		printf "%s/%s/%s\n",
			$tm[3], $text{"smonth_".($tm[4]+1)}, $tm[5]+1900;
		}
	elsif ($n eq "") { print "$text{'uedit_never'}\n"; }
	else { print "$text{'uedit_unknown'}\n"; }
	if ($uinfo{'max'} && $pft == 2) {
		print "<input type=checkbox name=forcechange value=1> ",
		      "$text{'uedit_forcechange'}\n";
		}
	print "</td>\n";

	if ($pft == 2) {
		print "<td>",&hlink("<b>$text{'expire'}</b>","expire"),
		      "</td>\n";
		if ($uinfo{'expire'}) {
			@tm = localtime(timelocal(gmtime($uinfo{'expire'} * 60*60*24)));
			$eday = $tm[3];
			$emon = $tm[4]+1;
			$eyear = $tm[5]+1900;
			}
		print "<td>";
		&date_input($eday, $emon, $eyear, 'expire');
		print "</td>\n";
		}
	else {
		print "<td>",&hlink("<b>$text{'ask'}</b>","ask"),"</td>\n";
		printf "<td><input type=radio name=ask value=1 %s> %s\n",
			$uinfo{'change'} eq '0' ? 'checked' : '', $text{'yes'};
		printf "<input type=radio name=ask value=0 %s> %s</td>\n",
			$uinfo{'change'} eq '0' ? '' : 'checked', $text{'no'};
		}
	print "</tr>\n";

	print "<tr> <td>",&hlink("<b>$text{'min'}</b>","min"),"</td>\n";
	printf "<td><input size=5 name=min value=\"%s\"></td>\n",
		$n eq "" ? $config{'default_min'} : $uinfo{'min'};

	print "<td>",&hlink("<b>$text{'max'}</b>","max"),"</td>\n";
	printf "<td><input size=5 name=max value=\"%s\"></td></tr>\n",
		$n eq "" ? $config{'default_max'} : $uinfo{'max'};

	if ($pft == 2) {
		# SCO does not have these password file options
		print "<tr> <td>",&hlink("<b>$text{'warn'}</b>","warn"),"</td>\n";
		printf "<td><input size=5 name=warn value=\"%s\"></td>\n",
			$n eq "" ? $config{'default_warn'} : $uinfo{'warn'};

		print "<td>",&hlink("<b>$text{'inactive'}</b>","inactive"),"</td>\n";
		printf "<td><input size=5 name=inactive value=\"%s\"></td></tr>\n",
			$n eq "" ? $config{'default_inactive'} : $uinfo{'inactive'};
		}

	print "</table></td></tr></table><p>\n";
	}
elsif ($pft == 4 && $access{'peopt'}) {
	# System has extra AIX password information
	print "<table border width=100%>\n";
	print "<tr $tb> <td><b>$text{'uedit_passopts'}</b></td> </tr>\n";
	print "<tr $cb> <td><table width=100%>\n";

	print "<tr> <td>",&hlink("<b>$text{'change'}</b>","change"),
	      "</td>\n";
	if ($uinfo{'change'}) {
		@tm = localtime($uinfo{'change'});
		printf "<td>%s/%s/%s %2.2d:%2.2d:%2.2d</td>\n",
			$tm[3], $text{"smonth_".($tm[4]+1)}, $tm[5]+1900,
			$tm[2], $tm[1], $tm[0];
		}
	elsif ($n eq "") { print "<td>$text{'uedit_never'}</td>\n"; }
	else { print "<td>$text{'uedit_unknown'}</td>\n"; }

	print "<td>",&hlink("<b>$text{'expire'}</b>","expire"),"</td>\n";
	if ($uinfo{'expire'}) {
		$uinfo{'expire'} =~ /^(\d\d)(\d\d)(\d\d)(\d\d)(\d\d)/;
		$emon = $1;
		$eday = $2;
		$ehour = $3;
		$emin = $4;
		$eyear = $5;
		if ($eyear > 38) {
			$eyear += 1900;
			}
		else {
			$eyear += 2000;
			}
		}
	$emon =~ s/0(\d)/$1/;	# strip leading 0 
	print "<td>";
	&date_input($eday, $emon, $eyear, 'expire');
	print " &nbsp; <input name=expireh size=3 value=\"$ehour\">";
	print "<b>:</b><input name=expiremi size=3 value=\"$emin\"></td> </tr>\n";

	print "<tr> <td>",&hlink("<b>$text{'min_weeks'}</b>","min_weeks"),"</td>\n";
	print "<td><input size=5 name=min value=\"$uinfo{'min'}\"></td>\n";

	print "<td>",&hlink("<b>$text{'max_weeks'}</b>","max_weeks"),"</td>\n";
	print "<td><input size=5 name=max value=\"$uinfo{'max'}\"></td></tr>\n";

	print "<tr> <td valign=top>",&hlink("<b>$text{'warn'}</b>","warn"),"</td>\n";
	print "<td valign=top><input size=5 name=warn value=\"$uinfo{'warn'}\"></td>\n";

	print "<td valign=top>",&hlink("<b>$text{'flags'}</b>","flags"),
	      "</td> <td>\n";
	printf "<input type=checkbox name=flags value=admin %s> %s<br>\n",
		$uinfo{'admin'} ? 'checked' : '', $text{'uedit_admin'};
	printf "<input type=checkbox name=flags value=admchg %s> %s<br>\n",
		$uinfo{'admchg'} ? 'checked' : '', $text{'uedit_admchg'};
	printf "<input type=checkbox name=flags value=nocheck %s> %s\n",
		$uinfo{'nocheck'} ? 'checked' : '', $text{'uedit_nocheck'};
	print "</td> </tr>\n";

	print "</table></td></tr></table><p>\n";
	}

# Output group memberships
print "<table border width=100%>\n";
print "<tr $tb> <td><b>$text{'uedit_gmem'}</b></td> </tr>\n";
print "<tr $cb> <td><table width=100%>\n";
print "<tr> <td valign=top>",&hlink("<b>$text{'group'}</b>","group"),
      "</td> <td valign=top>\n";
if ($n eq "" && $access{'gcreate'}) {
	printf "<input type=radio name=gidmode value=2 %s> %s<br>\n",
		$config{'new_user_group'} ? 'checked' : '', $text{'uedit_samg'};
	printf "<input type=radio name=gidmode value=1> %s\n",
		$text{'uedit_newg'};
	print "<input name=newgid size=8><br>\n";
	printf "<input type=radio name=gidmode value=0 %s> %s\n",
		$config{'new_user_group'} ? '' : 'checked', $text{'uedit_oldg'};
	}
if ($access{'ugroups'} eq "*" || $access{'uedit_gmode'} >= 3) {
	printf "<input name=gid size=8 value=\"%s\">\n",
		$n eq "" ? $config{'default_group'}
			 : scalar(&my_getgrgid($uinfo{'gid'}));
	print "<input type=button onClick='ifield = document.forms[0].gid; chooser = window.open(\"my_group_chooser.cgi?multi=0&group=\"+escape(ifield.value), \"chooser\", \"toolbar=no,menubar=no,scrollbars=yes,width=300,height=200\"); chooser.ifield = ifield; window.ifield = ifield' value=\"...\"></td>\n";
	}
else {
	print "<select name=gid>\n";
	local $cg = %uinfo ? &my_getgrgid($uinfo{'gid'}) : undef;
	@gl = &unique($cg ? ($cg) : (), split(/\s+/, $access{'ugroups'}));
	foreach $g (@gl) {
		printf "<option %s>%s\n",
			$cg eq $g ? "selected" : "", $g;
		}
	print "</select></td>\n";
	}

print "<td valign=top>",&hlink("<b>$text{'uedit_2nd'}</b>","2nd"),"</td>\n";
print "<td><select name=sgid multiple size=5>\n";
@glist = &list_groups();
@glist = sort { $a->{'group'} cmp $b->{'group'} } @glist
	if ($config{'sort_mode'});
@defsecs = split(/\s+/, $config{'default_secs'});
foreach $g (@glist) {
	@mems = split(/,/ , $g->{'members'});
	local $ismem = &indexof($uinfo{'user'}, @mems) >= 0;
	if ($n eq "") {
		$ismem = 1 if (&indexof($g->{'group'}, @defsecs) >= 0);
		}
	next if (!&can_use_group(\%access, $g->{'group'}) && !$ismem);
	printf "<option value=\"$g->{'group'}\" %s>$g->{'group'} ($g->{'gid'})\n",
		$ismem ? "selected" : "";
	}
print "</select></td> </tr>\n";
print "</table></td></tr></table><p>\n";

if ($n ne "") {
	# Editing a user - show options for moving home directory, changing IDs
	# and updating in other modules
	if ($access{'movehome'} == 1 || $access{'chuid'} == 1 ||
	    $access{'chgid'} == 1 || $access{'mothers'} == 1) {
		print "<table border width=100%>\n";
		print "<tr $tb> <td><b>$text{'onsave'}</b></td> </tr>\n";
		print "<tr $cb> <td><table>\n";

		if ($access{'movehome'} == 1) {
			print "<tr> <td>",&hlink($text{'uedit_movehome'}, "movehome"),"</td>\n";
			print "<td><input type=radio name=movehome value=1 checked> $text{'yes'}</td>\n";
			print "<td><input type=radio name=movehome value=0> $text{'no'}</td> </tr>\n";
			}

		if ($access{'chuid'} == 1) {
			print "<tr> <td>",&hlink($text{'uedit_chuid'},"chuid"),"</td>\n";
			print "<td><input type=radio name=chuid value=0> $text{'no'}</td>\n";
			print "<td><input type=radio name=chuid value=1 checked> ",
			      "$text{'home'}</td>\n";
			print "<td><input type=radio name=chuid value=2> ",
			      "$text{'uedit_allfiles'}</td></tr>\n";
			}

		if ($access{'chgid'} == 1) {
			print "<tr> <td>",&hlink($text{'chgid'},"chgid"),"</td>\n";
			print "<td><input type=radio name=chgid value=0> $text{'no'}</td>\n";
			print "<td><input type=radio name=chgid value=1 checked> ".
			      "$text{'home'}</td>\n";
			print "<td><input type=radio name=chgid value=2> ",
			      "$text{'uedit_allfiles'}</td></tr>\n";
			}

		if ($access{'mothers'} == 1) {
			print "<tr> <td>",&hlink($text{'uedit_mothers'},"others"),"</td>\n";
			printf "<td><input type=radio name=others value=1 %s> $text{'yes'}</td>\n",
				$config{'default_other'} ? "checked" : "";
			printf "<td><input type=radio name=others value=0 %s> $text{'no'}</td> </tr>\n",
				$config{'default_other'} ? "" : "checked";
			}

		print "</table></td> </tr></table><p>\n";
		}
	}
else {
	# Creating a user - show options for creating home directory, copying
	# skel files and creating in other modules
	if ($access{'makehome'} == 1 || $access{'copy'} == 1 ||
	    $access{'cothers'} == 1) {
		print "<table border width=100%>\n";
		print "<tr $tb> <td><b>$text{'uedit_oncreate'}</b></td> </tr>\n";
		print "<tr $cb> <td><table>\n";

		if ($access{'makehome'} == 1) {
			print "<tr> <td>",&hlink($text{'uedit_makehome'},"makehome"),"</td>\n";
			print "<td><input type=radio name=makehome value=1 checked> $text{'yes'}</td>\n";
			print "<td><input type=radio name=makehome value=0> $text{'no'}</td> </tr>\n";
			}

		if ($config{'user_files'} =~ /\S/ && $access{'copy'} == 1) {
			print "<tr> <td>",&hlink($text{'uedit_copy'},
						 "copy_files"),"</td>\n";
			print "<td><input type=radio name=copy_files ",
			      "value=1 checked> $text{'yes'}</td>\n";
			print "<td><input type=radio name=copy_files ",
			      "value=0> $text{'no'}</td> </tr>\n";
			}

		if ($access{'cothers'} == 1) {
			print "<tr> <td>",&hlink($text{'uedit_cothers'},"others"),"</td>\n";
			printf "<td><input type=radio name=others value=1 %s> $text{'yes'}</td>\n",
				$config{'default_other'} ? "checked" : "";
			printf "<td><input type=radio name=others value=0 %s> $text{'no'}</td> </tr>\n",
				$config{'default_other'} ? "" : "checked";
			}

		print "</table></td> </tr></table><p>\n";
		}
	}
if ($n ne "") {
	print "<table width=100%>\n";
	print "<tr> <td><input type=submit value=\"$text{'save'}\"></td>\n";

	print "</form><form action=\"list_logins.cgi\">\n";
	print "<input type=hidden name=username value=\"$uinfo{'user'}\">\n";
	print "<td align=center>\n";
	print "<input type=submit value=\"$text{'uedit_logins'}\"></td>\n";

	&read_acl(\%acl);
	if ($acl{$base_remote_user,"mailboxes"} &&
	    &foreign_installed("mailboxes", 1)) {
		# Link to the mailboxes module, if installed
		print "</form><form action=../mailboxes/list_mail.cgi>\n";
		print "<input type=hidden name=user value='$uinfo{'user'}'>\n";
		print "<td align=center>\n";
		print "<input type=submit value='$text{'uedit_mail'}'></td>\n";
		}

	print "</form><form action=\"delete_user.cgi\">\n";
	print "<input type=hidden name=num value=\"$n\">\n";
	print "<input type=hidden name=user value=\"$uinfo{'user'}\">\n";
	print "<td align=right><input type=submit value=\"$text{'delete'}\"></td> </tr>\n";
	print "</form></table><p>\n";
	}
else {
	print "<input type=submit value=\"$text{'create'}\"></form><p>\n";
	}

&ui_print_footer("", $text{'index_return'});


