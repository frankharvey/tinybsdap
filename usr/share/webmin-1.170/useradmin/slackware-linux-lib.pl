# linux-lib.pl
# Functions for reading linux format last output

# passfiles_type()
# Returns 0 for old-style passwords (/etc/passwd only), 1 for FreeBSD-style
# (/etc/master.passwd) and 2 for SysV (/etc/passwd & /etc/shadow)
sub passfiles_type
{
return &password_file($config{'shadow_file'}) ? 2 : 0;
}

# groupfiles_type()
# Returns 0 for normal group file (/etc/group only) and 2 for shadowed
# (/etc/group and /etc/gshadow)
sub groupfiles_type
{
return &password_file($config{'gshadow_file'}) ? 2 : 0;
}

# open_last_command(handle, user)
sub open_last_command
{
local ($fh, $user) = @_;
open($fh, "last $user |");
}

# read_last_line(handle)
# Parses a line of output from last into an array of
#  user, tty, host, login, logout, period
sub read_last_line
{
$fh = $_[0];
while(1) {
	chop($line = <$fh>);
	if (!$line) { return (); }
	if ($line =~ /system boot/) { next; }
	if ($line =~ /^(\S+)\s+(\S+)\s+(\S+)?\s+(\S+\s+\S+\s+\d+\s+\d+:\d+)\s+\-\s+(\S+)\s+\((\d+:\d+)\)/) {
		return ($1, $2, $3, $4, $5 eq "down" ? "Shutdown" : $5, $6);
		}
	elsif ($line =~ /^(\S+)\s+(\S+)\s+(\S+)?\s+(\S+\s+\S+\s+\d+\s+\d+:\d+)\s+still/) {
		return ($1, $2, $3, $4);
		}
	}
}

# logged_in_users()
# Returns a list of hashes containing details of logged-in users
sub logged_in_users
{
local @rv;
open(WHO, "who |");
while(<WHO>) {
	if (/^(\S+)\s+(\S+)\s+(\S+\s+\d+\s+\d+:\d+)\s+(\((\S+)\))?/) {
		push(@rv, { 'user' => $1, 'tty' => $2,
			    'when' => $3, 'from' => $5 });
		}
	}
close(WHO);
return @rv;
}

# use_md5()
# Returns 1 if pam is set up to use MD5 encryption
sub use_md5
{
local $md5 = 0;
if (&foreign_check("pam")) {
	# Use the PAM module if we can
	&foreign_require("pam", "pam-lib.pl");
	local @conf = &foreign_call("pam", "get_pam_config");
	local ($svc) = grep { $_->{'name'} eq 'passwd' } @conf;
	LOOP: foreach $m (@{$svc->{'mods'}}) {
		if ($m->{'type'} eq 'password') {
			if ($m->{'args'} =~ /md5/) { $md5++; }
			elsif ($m->{'module'} =~ /pam_stack\.so/ &&
			       $m->{'args'} =~ /service=(\S+)/) {
				# Referred to another service!
				($svc) = grep { $_->{'name'} eq $1 } @conf;
				if ($svc) { goto LOOP }
				else { last; }
				}
			}
		}
	}
elsif (open(PAM, "/etc/pam.d/passwd")) {
	# Otherwise try to check the PAM file directly
	while(<PAM>) {
		s/#.*$//g;
		$md5++ if (/^password.*md5/);
		}
	close(PAM);
	}
if (open(DEFS, "/etc/login.defs")) {
	# The login.defs file is used on debian sometimes
	while(<DEFS>) {
		s/#.*$//g;
		$md5++ if (/MD5_CRYPT_ENAB\s+yes/i);
		}
	close(DEFS);
	}
return $md5;
}

1;
