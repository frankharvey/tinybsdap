#!/usr/local/bin/perl
# clone_mod.cgi
# Clone an existing module under a new name

require './webmin-lib.pl';
&ReadParse();
&error_setup($text{'clone_err'});

# Symlink the code directory
$src = $in{'mod'};
%minfo = &get_module_info($src);
$count = 2;
do {
	$dst = $src.$count;
	$count++;
	} while(-d "../$dst");
symlink($src, "../$dst") || &error(&text('clone_elink', $!));

# Symlink in the theme directory
if ($gconfig{'theme'}) {
	unlink("../$gconfig{'theme'}/$dst");
	symlink($src, "../$gconfig{'theme'}/$dst");
	}

# Copy the config directory
mkdir("$config_directory/$dst", 0700);
$out = `( (cd $config_directory/$src ; tar cf - .) | (cd $config_directory/$dst ; tar xpf -) ) 2>&1`;
if ($?) {
	&error(&text('clone_ecopy', $out));
	}
$in{'desc'} = &text('clone_desc', $minfo{'desc'}) if (!$in{'desc'});
open(CLONE, ">$config_directory/$dst/clone");
print CLONE "desc=$in{'desc'}\n";
close(CLONE);

# Delete .lock files from the config directory
system("(find '$config_directory/$dst' -name '*.lock' | xargs rm -f) >/dev/null 2>&1");

# Grant access to the clone to this user
&read_acl(undef, \%acl);
open(ACL, "> ".&acl_filename());
foreach $u (keys %acl) {
	local @mods = @{$acl{$u}};
	if ($u eq $base_remote_user) {
		@mods = &unique(@mods, $dst);
		}
	print ACL "$u: ",join(' ', @mods),"\n";
	}
close(ACL);

if ($in{'cat'} ne '*') {
	# Assign to category
	&lock_file("$config_directory/webmin.cats");
	&read_file("$config_directory/webmin.cats", \%cats);
	$cats{$dst} = $in{'cat'};
	&write_file("$config_directory/webmin.cats", \%cats);
	&unlock_file("$config_directory/webmin.cats");
	}

&webmin_log("clone", undef, $in{'mod'}, { 'desc' => $minfo{'desc'},
					  'dst' => $dst,
					  'dstdesc' => $in{'desc'} });
&flush_webmin_caches();
&redirect("");

