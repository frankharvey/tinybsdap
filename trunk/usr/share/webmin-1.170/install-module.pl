#!/usr/bin/perl
# install-module.pl
# Install a single module file

# Check arguments
if (@ARGV > 2 || !@ARGV) {
	die "usage: install-module.pl <module.wbm> [config_directory]";
	}
$file = $ARGV[0];
$config = $ARGV[1] ? $ARGV[1] : "/etc/webmin";
-r $file || die "$file does not exist";
open(CONF, "$config/miniserv.conf") ||
	die "Failed to read $config/miniserv.conf - maybe $config is not a Webmin config directory";
while(<CONF>) {
	s/\r|\n//g;
	if (/^root=(.*)/) {
		$root = $1;
		}
	}
close(CONF);
-d $root || die "Webmin directory $root does not exist";
chop($var = `cat $config/var-path`);

if ($file !~ /^\//) {
	chop($pwd = `pwd`);
	$file = "$pwd/$file";
	}

# Set up webmin environment
$ENV{'WEBMIN_CONFIG'} = $config;
$ENV{'WEBMIN_VAR'} = $var;
$no_acl_check++;
chdir($root);
$0 = "$root/install-module.pl";
do './web-lib.pl';
&init_config();

# Install it, using the standard function
&foreign_require("webmin", "webmin-lib.pl");
$rv = &webmin::install_webmin_module($file, 0, 0, [ ]);
if (ref($rv)) {
	for($i=0; $i<@{$rv->[0]}; $i++) {
		printf "Installed %s in %s (%d kb)\n",
			$rv->[0]->[$i],
			$rv->[1]->[$i],
			$rv->[2]->[$i];
		}
	}
else {
	print STDERR "Install failed : $rv\n";
	}

