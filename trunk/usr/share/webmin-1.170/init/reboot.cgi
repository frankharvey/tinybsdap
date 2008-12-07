#!/usr/bin/perl
# reboot.cgi
# Reboot the system immediately..

require './init-lib.pl';
&ReadParse();
%access = &get_module_acl();
$access{'reboot'} || &error($text{'reboot_ecannot'});
&ui_print_header(undef, $text{'reboot_title'}, "");
print "<p>\n";
$ttcmd = "<tt>$config{'reboot_command'}</tt>";
if ($in{'confirm'}) {
	print "<font size=+1>",&text('reboot_exec', $ttcmd),"</font><p>\n";
	&system_logged("$config{'reboot_command'} >/dev/null 2>/dev/null");
	&webmin_log("reboot");
	}
else {
	print "<font size=+1>",&text('reboot_rusure', $ttcmd),"</font>\n";
	print "<center><form action=reboot.cgi>\n";
	print "<input type=submit value=\"$text{'reboot_ok'}\" name=confirm>\n";
	print "</form></center>\n";
	}
&ui_print_footer("", $text{'index_return'});

