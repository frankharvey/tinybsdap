# log_parser.pl
# Functions for parsing this module's logs

do 'init-lib.pl';

# parse_webmin_log(user, script, action, type, object, &params)
# Converts logged information from this module into human-readable form
sub parse_webmin_log
{
local ($user, $script, $action, $type, $object, $p) = @_;
if ($action eq 'modify') {
	if ($p->{'old'} ne $p->{'name'}) {
		return &text('log_rename', "<tt>$p->{'old'}</tt>",
					   "<tt>$p->{'name'}</tt>");
		}
	else {
		return &text('log_modify', "<tt>$object</tt>");
		}
	}
elsif ($action eq 'create') {
	return &text('log_create', "<tt>$object</tt>");
	}
elsif ($action eq 'delete') {
	return &text('log_delete', "<tt>$object</tt>");
	}
elsif ($action eq 'start') {
	return &text('log_start', "<tt>$object</tt>");
	}
elsif ($action eq 'stop') {
	return &text('log_stop', "<tt>$object</tt>");
	}
elsif ($action eq 'reboot') {
	return $text{'log_reboot'};
	}
elsif ($action eq 'shutdown') {
	return $text{'log_shutdown'};
	}
elsif ($action eq 'local') {
	return $text{'log_local'};
	}
elsif ($action eq 'bootup') {
	return &text('log_bootup', join(" , ", map { "<tt>$_</tt>" } keys %$p));
	}
else {
	return undef;
	}
}

