#!/usr/local/bin/perl
# list_logins.cgi
# Display the last login locations, tty, login time and duration

require './user-lib.pl';
&ReadParse();
$u = $in{'username'};
%access = &get_module_acl();
if (!$access{'logins'}) {
	&error($text{'logins_elist'});
	}
elsif ($access{'logins'} ne "*") {
	$u || &error($text{'logins_elist'});
	local @ul = split(/\s+/, $access{'logins'});
	&indexof($u,@ul) >= 0 ||
		&error(&text('logins_elistu', $u));
	}

&ui_print_header(undef, $text{'logins_title'}, "", "list_logins");

if ($u) { print "<h3>",&text('logins_head', $u),"</h3>\n"; }
print "<table border width=100%> <tr $tb>\n";
if (!$u) { print "<td><b>$text{'user'}</b></td>\n"; }
print "<td><b>$text{'logins_from'}</b></td>\n";
print "<td><b>$text{'logins_tty'}</b></td>\n";
print "<td><b>$text{'logins_in'}</b></td>\n";
print "<td><b>$text{'logins_out'}</b></td>\n";
print "<td><b>$text{'logins_for'}</b></td> </tr>\n";
&open_last_command(LAST, $u);
while(@last = &read_last_line(LAST)) {
	print "<tr $cb>", $u ? ""
			     : "<td><tt>".&html_escape($last[0])."</tt></td>";
	print "<td><tt>", $last[2] ? &html_escape($last[2])
				   : $text{'logins_local'},
	      "</tt></td> <td><tt>",&html_escape($last[1]),"</tt></td> ",
	      "<td><tt>",&html_escape($last[3]),"</tt></td>\n";
	if ($last[4]) {
		print "<td><tt>",&html_escape($last[4]),"</tt></td> ",
		      "<td><tt>",&html_escape($last[5]),"</tt></td> </tr>\n";
		}
	else {
		print "<td colspan=2><tt>$text{'logins_still'}",
		      "</tt></td> </tr>\n";
		}
	$foundany++;
	if ($config{'last_count'} && ++$count >= $config{'last_count'}) {
		# Displayed maximum number
		last;
		}
	}
close(LAST);
if (!$foundany) {
	printf "<tr $cb> <td colspan=%d>$text{'logins_none'}</td> </tr>\n",
		$u ? 5 : 6;
	}
print "</table><p>\n";

&ui_print_footer("", $text{'index_return'});

