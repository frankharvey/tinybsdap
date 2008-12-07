#!/usr/local/bin/perl
# change_ssl.cgi
# Enable or disable SSL support

require './webmin-lib.pl';
&ReadParse();
&error_setup($text{'ssl_err'});

&lock_file($ENV{'MINISERV_CONFIG'});
&get_miniserv_config(\%miniserv);
$miniserv{'ssl'} = $in{'ssl'};
$key = `cat '$in{'key'}' 2>&1`;
$key =~ /BEGIN RSA PRIVATE KEY/i || &error(&text('ssl_ekey', $in{'key'}));
$miniserv{'keyfile'} = $in{'key'};
if ($in{'cert_def'}) {
	$key =~ /BEGIN CERTIFICATE/ || &error(&text('ssl_ecert', $in{'key'}));
	delete($miniserv{'certfile'});
	}
else {
	$cert = `cat '$in{'cert'}' 2>&1`;
	$cert =~ /BEGIN CERTIFICATE/ || &error(&text('ssl_ecert',$in{'cert'}));
	$miniserv{'certfile'} = $in{'cert'};
	}
$miniserv{'ssl_redirect'} = $in{'ssl_redirect'};
foreach $ec (split(/[\r\n]+/, $in{'extracas'})) {
	-r $ec && !-d $ec || &error(&text('ssl_eextraca', $ec));
	push(@extracas, $ec);
	}
$miniserv{'extracas'} = join("\t", @extracas);
&put_miniserv_config(\%miniserv);
&unlock_file($ENV{'MINISERV_CONFIG'});

$SIG{'TERM'} = 'IGNORE';	# stop process from being killed by restart
&restart_miniserv();
&webmin_log("ssl", undef, undef, \%in);

$url = "$ENV{'SERVER_NAME'}:$miniserv{'port'}/webmin/";
if ($in{'ssl'}) { &redirect("https://$url"); }
else { &redirect("http://$url"); }

