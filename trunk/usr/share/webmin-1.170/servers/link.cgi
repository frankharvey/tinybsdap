#!/usr/bin/perl
# link.cgi
# Forward the URL from path_info on to another webmin server

require './servers-lib.pl';
$ENV{'PATH_INFO'} =~ /^\/(\d+)(.*)$/ ||
	&error("Bad PATH_INFO : $ENV{'PATH_INFO'}");
$id = $1;
$path = $2 ? &urlize("$2") : '/';
$path =~ s/^%2F/\//;
if ($ENV{'QUERY_STRING'}) {
	$path .= '?'.$ENV{'QUERY_STRING'};
	}
elsif (@ARGV) {
	$path .= '?'.join('+', @ARGV);
	}
$s = &get_server($id);
&can_use_server($s) || &error($text{'link_ecannot'});
$url = "/$module_name/link.cgi/$s->{'id'}";
$| = 1;
$meth = $ENV{'REQUEST_METHOD'};

if ($s->{'autouser'}) {
	# Login is variable .. check if we have it yet
	# XXX logout?
	# XXX upload fixed version
	if ($ENV{'HTTP_COOKIE'} =~ /$id=(\S+)/) {
		# Yes - set the login and password to use
		($user, $pass) = split(/:/, &decode_base64("$1"));
		}
	else {
		# No - need to display a login form
		&ui_print_header(undef, $text{'login_title'}, "");
		print "<center>",&text('login_desc', "<tt>$s->{'host'}</tt>"),
		      "</center><p>\n";
		print "<form action=/$module_name/login.cgi method=post>\n";
		print "<input type=hidden name=id value='$id'>\n";
		print "<center><table border>\n";
		print "<tr $tb> <td><b>$text{'login_header'}</b></td> </tr>\n";
		print "<tr $cb> <td><table cellpadding=2>\n";
		print "<tr> <td><b>$text{'login_user'}</b></td>\n";
		print "<td><input name=user size=20></td> </tr>\n";
		print "<tr> <td><b>$text{'login_pass'}</b></td>\n";
		print "<td><input name=pass size=20 type=password></td>\n";
		print "</tr> </table></td></tr></table>\n";
		print "<input type=submit value='$text{'login_login'}'>\n";
		print "<input type=reset value='$text{'login_clear'}'>\n";
		print "</center></form>\n";
		&ui_print_footer("", $text{'index_return'});
		exit;
		}
	}
else {
	# Login is fixed
	$user = $s->{'user'};
	$pass = $s->{'pass'};
	}

# Connect to the server
$con = &make_http_connection($s->{'host'}, $s->{'port'}, $s->{'ssl'},
			     $meth, $path);
&error($con) if (!ref($con));

# Send request headers
&write_http_connection($con, "Host: $s->{'host'}\r\n");
&write_http_connection($con, "User-agent: Webmin\r\n");
$auth = &encode_base64("$user:$pass");
$auth =~ s/\n//g;
&write_http_connection($con, "Authorization: basic $auth\r\n");
&write_http_connection($con, sprintf(
			"Webmin-servers: %s://%s:%d/$module_name/\n",
			$ENV{'HTTPS'} eq "ON" ? "https" : "http",
			$ENV{'SERVER_NAME'}, $ENV{'SERVER_PORT'}));
$cl = $ENV{'CONTENT_LENGTH'};
&write_http_connection($con, "Content-length: $cl\r\n") if ($cl);
&write_http_connection($con, "Content-type: $ENV{'CONTENT_TYPE'}\r\n")
	if ($ENV{'CONTENT_TYPE'});
&write_http_connection($con, "\r\n");
if ($cl) {
	read(STDIN, $post, $cl);
	&write_http_connection($con, $post);
	}

# read back the headers
$dummy = &read_http_connection($con);
while(1) {
	($headline = &read_http_connection($con)) =~ s/\r|\n//g;
	last if (!$headline);
	$headline =~ /^(\S+):\s+(.*)$/ || &error("Bad header");
	$header{lc($1)} = $2;
	$headers .= $headline."\n";
	}

$defport = $s->{'ssl'} ? 443 : 80;
if ($header{'location'} =~ /^(http|https):\/\/$s->{'host'}:$s->{'port'}(.*)$/ ||
    $header{'location'} =~ /^(http|https):\/\/$s->{'host'}(.*)/ &&
    $s->{'port'} == $defport) {
	# fix a redirect
	&redirect("$url$2");
	exit;
	}
elsif ($header{'www-authenticate'}) {
	# Invalid login
	if ($s->{'autouser'}) {
		print "Set-Cookie: $id=; path=/\n";
		&error(&text('link_eautologin', $s->{'host'},
		     "$gconfig{'webprefix'}/$module_name/link.cgi/$id/"));
		}
	else {
		&error(&text('link_elogin', $s->{'host'}, $user));
		}
	}
else {
	# just output the headers
	print $headers,"\n";
	}

# read back the rest of the page
if ($header{'content-type'} =~ /text\/html/ && !$header{'x-no-links'}) {
	while($_ = &read_http_connection($con)) {
		s/src='(\/[^']*)'/src='$url$1'/gi;
		s/src="(\/[^"]*)"/src="$url$1"/gi;
		s/src=(\/[^ "'>]*)/src=$url$1/gi;
		s/href='(\/[^']*)'/href='$url$1'/gi;
		s/href="(\/[^"]*)"/href="$url$1"/gi;
		s/href=(\/[^ >"']*)/href=$url$1/gi;
		s/action='(\/[^']*)'/action='$url$1'/gi;
		s/action="(\/[^"]*)"/action="$url$1"/gi;
		s/action=(\/[^ "'>]*)/action=$url$1/gi;
		s/\.location\s*=\s*'(\/[^']*)'/.location='$url$1'/gi;
		s/\.location\s*=\s*"(\/[^']*)"/.location="$url$1"/gi;
		s/window.open\("(\/[^"]*)"/window.open\("$url$1"/gi;
		s/name=return\s+value="(\/[^"]*)"/name=return value="$url$1"/gi;
		print;
		}
	}
else {
	while($buf = &read_http_connection($con, 1024)) {
		print $buf;
		}
	}
&close_http_connection($con);

