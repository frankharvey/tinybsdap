#!/usr/bin/perl
# date_chooser.cgi
# Display a table of days in the current month

require './web-lib.pl';
require 'timelocal.pl';
&init_config();
&ReadParse();
&PrintHeader();

@daysin = ( 31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31 );
$daysin[1] = $in{'year'}%400 == 0 ? 29 :
	     $in{'year'}%100 == 0 ? 28 :
	     $in{'year'}%4 == 0 ? 29 : 28;

@tm = localtime(time());
if ($in{'day'} !~ /^\d+$/ || $in{'day'} < 1 || $in{'year'} !~ /^\d+$/) {
	$in{'day'} = $tm[3];
	$in{'month'} = $tm[4];
	$in{'year'} = $tm[5]+1900;
	}
if ($in{'day'} > $daysin[$in{'month'}]) {
	$in{'day'} = $daysin[$in{'month'}];
	}
$tm = timelocal(0, 0, 12, $in{'day'}, $in{'month'}, $in{'year'});

print <<EOF;
<html><head>
<script>
function newmonth(m)
{
location = "date_chooser.cgi?day=$in{'day'}&month="+m.selectedIndex+"&year=$in{'year'}";
}
function newyear(y)
{
location = "date_chooser.cgi?day=$in{'day'}&month=$in{'month'}&year="+(y.selectedIndex+$in{'year'}-10);
}
function newday(d)
{
opener.dfield.value = d;
opener.mfield.selectedIndex = $in{'month'};
opener.yfield.value = $in{'year'};
close();
}
</script>
</head><body bgcolor=#ffffff>
<form><table border width=100%>
<tr> <td colspan=7 align=center><select name=year onChange='newyear(this)'>
EOF
for($i=$in{'year'}-10; $i<=$in{'year'}+10; $i++) {
	printf "<option %s>%s\n",
		$i == $in{'year'} ? 'selected' : '', $i;
	}
print "</select> <select name=month onChange='newmonth(this)'>\n";
for($i=0; $i<12; $i++) {
	printf "<option value=%s %s>%s\n",
		$i, $i == $in{'month'} ? 'selected' : '',
		$text{"month_".($i+1)};
	}
print "</select></td> </tr>\n";

print "<tr>\n";
for($i=0; $i<7; $i++) {
	print "<td><b>",$text{"sday_$i"},"</b></td>\n";
	}
print "</tr>\n";

@first = localtime($tm - ($in{'day'}-1)*24*60*60);
$count = -$first[6] + 1;
for($y=0; $y<6; $y++) {
	print "<tr>\n";
	for($x=0; $x<7; $x++) {
		if ($count < 1 || $count > $daysin[$in{'month'}]) {
			print "<td align=center></td>\n";
			}
		else {
			printf "<td align=center %s><a href='' onClick='newday($count)'>%s</a></td>\n", $in{'day'} == $count ? $cb : '', $count;
			}
		$count++;
		}
	print "</tr>\n";
	}
print "</table></form>\n";
print "</body></html>\n";

