# log_parser.pl
# Functions for parsing this module's logs

do 'servers-lib.pl';

# parse_webmin_log(user, script, action, type, object, &params)
# Converts logged information from this module into human-readable form
sub parse_webmin_log
{
local ($user, $script, $action, $type, $object, $p) = @_;
$object = &html_escape($object);
if ($action eq 'modify') {
	return &text('log_modify', "<tt>$object</tt>");
	}
elsif ($action eq 'create') {
	return &text('log_create', "<tt>$object</tt>");
	}
elsif ($action eq 'find') {
	return &text('log_find', "<tt>$object</tt>");
	}
elsif ($action eq 'delete') {
	return &text('log_delete', "<tt>$object</tt>");
	}
else {
	return undef;
	}
}

