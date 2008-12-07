# gnupg-lib.pl
# Functions for managing gnupg keys, signing, encrypting and so on

if (!$module_name) {
	# Only do this if we are the primary library for the usermin gnupg mod
	do '../web-lib.pl';
	&init_config();
	require '../ui-lib.pl';
	&switch_to_remote_user();
	&create_user_config_dirs();
	}
&foreign_require("proc", "proc-lib.pl");

$gpgpath = $config{'gpg'} || "gpg";

# list_keys()
# Returns an array of all GnuPG keys
sub list_keys
{
local (@rv, %kmap);
open(GPG, "$gpgpath --list-keys 2>/dev/null |");
while(<GPG>) {
	if (/^pub\s+(\S+)\/(\S+)\s+(\S+)\s+(.*)\s+<(\S+)>/ ||
	    /^pub\s+(\S+)\/(\S+)\s+(\S+)\s+(.*)/) {
		local $k = { 'size' => $1,
			     'key' => $2,
			     'date' => $3,
			     'name' => [ $4 ],
			     'email' => [ $5 ],
			     'index' => scalar(@rv) };
		$kmap{$k->{'key'}} = $k;
		while(1) {
			$_ = <GPG>;
			last if ($_ !~ /\S/);
			if (/^sub\s+(\S+)\/(\S+)\s+/) {
				push(@{$k->{'key2'}}, $2);
				}
			elsif (/^uid\s+(.*)\s+<(\S+)>/ ||
			       /^uid\s+(.*)/) {
				push(@{$k->{'name'}}, $1);
				push(@{$k->{'email'}}, $2);
				}
			}
		push(@rv, $k);
		}
	}
close(GPG);
open(GPG, "$gpgpath --list-secret-keys 2>/dev/null |");
while(<GPG>) {
	if (/^sec\s+(\S+)\/(\S+)\s+(\S+)\s+(.*)/ && $kmap{$2}) {
		$kmap{$2}->{'secret'}++;
		}
	}
close(GPG);
return @rv;
}

# list_secret_keys()
# List list_keys, but only returns secret ones
sub list_secret_keys
{
return grep { $_->{'secret'} } &list_keys();
}

# key_fingerprint(&key)
sub key_fingerprint
{
local $fp;
local $_;
open(GPG, "$gpgpath --fingerprint \"$_[0]->{'name'}->[0]\" |");
while(<GPG>) {
	if (/fingerprint\s+=\s+(.*)/) {
		$fp = $1;
		}
	}
close(GPG);
return $fp;
}

# get_passphrase(&key)
sub get_passphrase
{
open(PASS, "$user_module_config_directory/pass.$_[0]->{'key'}") ||
  open(PASS, "$user_module_config_directory/pass") || return undef;
local $pass = <PASS>;
close(PASS);
chop($pass);
return $pass;
}

# put_passphrase(pass, &key)
sub put_passphrase
{
open(PASS, ">$user_module_config_directory/pass.$_[1]->{'key'}");
print PASS $_[0],"\n";
close(PASS);
chmod(0700, "$user_module_config_directory/pass.$_[1]->{'key'}");
}

# encrypt_data(data, &result, &key|&keys, ascii)
# Encrypts some data with the given public key and returns the result, and
# returns an error message or undef on failure
sub encrypt_data
{
local $srcfile = &tempname();
local @keys = ref($_[2]) eq 'ARRAY' ? @{$_[2]} : ( $_[2] );
local $rcpt = join(" ", map { "--recipient \"$_->{'name'}->[0]\"" } @keys);
&write_entire_file($srcfile, $_[0]);
local $dstfile = &tempname();
local $ascii = $_[3] ? "--armor" : "";
local $comp = $config{'compress'} eq '' ? "" :
		" --compress-algo $config{'compress'}";
local $cmd = "$gpgpath --output $dstfile $rcpt $ascii $comp --encrypt $srcfile";
local ($fh, $fpid) = &foreign_call("proc", "pty_process_exec", $cmd);
while(1) {
	$rv = &wait_for($fh, "anyway");
	if ($rv == 0) {
		syswrite($fh, "yes\n", length("yes\n"));
		}
	elsif ($rv < 0) {
		last;
		}
	}
close($fh);
unlink($srcfile);
local $dst = &read_entire_file($dstfile);
unlink($dstfile);
if ($dst) {
	${$_[1]} = $dst;
	return undef;
	}
else {
	return $wait_for_input;
	}
}

# decrypt_data(data, &result)
# Decrypts some data encrypted for the current GnuPG user, and puts the results
# into &result. Returns an error message or undef on success.
sub decrypt_data
{
local $srcfile = &tempname();
&write_entire_file($srcfile, $_[0]);
local $dstfile = &tempname();
local $cmd = "$gpgpath --output $dstfile --decrypt $srcfile";
local ($fh, $fpid) = &foreign_call("proc", "pty_process_exec", $cmd);
local ($error, $seen_pass, $pass, $key, $keyid);
while(1) {
	local $rv = &wait_for($fh, "passphrase:", "key,\\s+ID\\s+(\\S+),", "failed.*\\n", "error.*\\n", "invalid.*\\n", "signal caught.*\\n");
	if ($rv == 0) {
		last if ($seen_pass++);
		sleep(1);
		syswrite($fh, "$pass\n", length("$pass\n"));
		}
	elsif ($rv == 1) {
		$keyid = $matches[1];
		($key) = grep { &indexof($matches[1], @{$_->{'key2'}}) >= 0 }
			      &list_secret_keys();
		$pass = &get_passphrase($key) if ($key);
		}
	elsif ($rv > 1) {
		$error++;
		last;
		}
	elsif ($rv < 0) {
		last;
		}
	}
close($fh);
unlink($srcfile);
local $dst = &read_entire_file($dstfile);
unlink($dstfile);
if (!$keyid) {
	return $text{'gnupg_ecryptid'};
	}
elsif (!$key) {
	return &text('gnupg_ecryptkey', "<tt>$keyid</tt>");
	}
elsif (!defined($pass)) {
	return &text('gnupg_ecryptpass', $key->{'name'}->[0]).". ".
	    &text('gnupg_canset', "/gnupg/edit_key.cgi?key=$key->{'key'}").".";
	}
elsif ($error || $seen_pass > 1) {
	return "<pre>$wait_for_input</pre>";
	}
else {
	${$_[1]} = $dst;
	return undef;
	}
}

# sign_data(data, \&result, &key, mode)
# Signs the given data and returns the result. Mode 0 = binary signature
# mode 1 = ascii signature at end, mode 2 = ascii signature only
sub sign_data
{
local $srcfile = &tempname();
&write_entire_file($srcfile, $_[0]);
local $dstfile = &tempname();
local $cmd;
if ($_[3] == 0) {
	$cmd = "$gpgpath --output $dstfile --default-key $_[2]->{'key'} --sign $srcfile";
	}
elsif ($_[3] == 1) {
	$cmd = "$gpgpath --output $dstfile --default-key $_[2]->{'key'} --clearsign $srcfile";
	}
elsif ($_[3] == 2) {
	$cmd = "$gpgpath --armor --output $dstfile --default-key $_[2]->{'key'} --detach-sig $srcfile";
	}
local ($fh, $fpid) = &foreign_call("proc", "pty_process_exec", $cmd);
local ($error, $seen_pass);
local $pass = &get_passphrase($_[2]);
if (!defined($pass)) {
	return $text{'gnupg_esignpass'}.". ".
	    &text('gnupg_canset', "/gnupg/edit_key.cgi?key=$_[2]->{'key'}").".";
	}
while(1) {
	$rv = &wait_for($fh, "passphrase:", "failed", "error");
	if ($rv == 0) {
		last if ($seen_pass++);
		sleep(1);
		syswrite($fh, "$pass\n", length("$pass\n"));
		}
	elsif ($rv > 0) {
		$error++;
		last;
		}
	elsif ($rv < 0) {
		last;
		}
	}
close($fh);
unlink($srcfile);
local $dst = &read_entire_file($dstfile);
unlink($dstfile);
if ($error || $seen_pass > 1) {
	return "<pre>$wait_for_input</pre>";
	}
else {
	${$_[1]} = $dst;
	return undef;
	}
}

# verify_data(data, [signature])
# Verifies the signature on some data, and returns a status code and a message
# code 0 = verified successfully, message contains signer
# code 1 = verified successfully but no trust chain, message contains signer
# code 2 = failed to verify, message contains signer
# code 3 = do not have signers public key, message contains ID
# code 4 = verification totally failed, message contains reason
sub verify_data
{
local $datafile = &tempname();
&write_entire_file($datafile, $_[0]);
local $cmd;
local $sigfile;
if (!$_[1]) {
	$cmd = "$gpgpath --verify $datafile";
	}
else {
	$sigfile = &tempname();
	&write_entire_file($sigfile, $_[1]);
	$cmd = "$gpgpath --verify $sigfile $datafile";
	}
#local ($fh, $fpid) = &foreign_call("proc", "pty_process_exec", $cmd);
#&wait_for($fh);
#close($fh);
#local $out = $wait_for_input;
local $out = `$cmd 2>&1 </dev/null`;
unlink($datafile);
unlink($sigfile) if ($sigfile);
if ($out =~ /BAD signature from "(.*)"/i) {
	return (2, $1);
	}
elsif ($out =~ /key ID (\S+).*\n.*not found/i) {
	return (3, $1);
	}
elsif ($out =~ /Good signature from "(.*)"/i) {
	local $signer = $1;
	if ($out =~ /warning/) {
		return (1, $signer);
		}
	else {
		return (0, $signer);
		}
	}
else {
	return (4, $out);
	}
}

# read_entire_file(file)
sub read_entire_file
{
local ($rv, $buf);
open(FILE, $_[0]) || return undef;
while(read(FILE, $buf, 1024) > 0) {
	$rv .= $buf;
	}
close(FILE);
return $rv;
}

# write_entire_file(file, data)
sub write_entire_file
{
open(FILE, ">$_[0]");
print FILE $_[1];
close(FILE);
}

# get_trust_level(&key)
# Returns the trust level of a key
sub get_trust_level
{
local $cmd = "$gpgpath --edit-key \"$_[0]->{'name'}->[0]\"";
local ($fh, $fpid) = &foreign_call("proc", "pty_process_exec", $cmd);
local $rv = &wait_for($fh, "trust:\\s+(.)", "command>");
local $tr;
if ($rv == 0) {
	$tr = $matches[1] eq "q" ? 1 : $matches[1] eq "n" ? 2 :
	      $matches[1] eq "m" ? 3 : $matches[1] eq "f" ? 4 : 0;
	}
else {
	$tr = -1;
	}
syswrite($fh, "quit\n", length("quit\n"));
close($fh);
return $tr;
}

1;

