#!/usr/bin/perl
# BibTex to HTML version 0.1
# Created by Christian Shelton (cshelton@cs.stanford.edu)
#       (c) August, 2002
#
# This script is released "as is" with no warentee specified or implied.
# No support is supplied with this script.
# You may copy it and modify it as you see fit provided you keep the 
# citation above.
# Neither Christian Shelton nor Stanford University are responsible for
# any consequences of the use of this script.
#

# HOW TO INSTALL/USE:
# (note this assumes some basic understanding of web servers, CGI scripts,
#  BibTex, and Perl)
#
# This script should be placed in a web directory that has CGI-Exec
# permissions (often called a cgi-bin directory).  In a separate directory
# (readable by the webserver), a bib file and the associated papers in
# downloadable form (.pdf, .ps, etc.) should be placed.  The
# configuration parameters below should be adjusted to point to that
# directory and the .bib file.
#
# The bib file should then be agumented with additional fields for each
# record.  In particular, the field "WWWfilebase" should indicate the base
# file name for the paper.  For example, if WWWfilebase is Shelton02, then
# all files beginning with Shelton02 will be included as downloadable versions
# of the paper (eg. Shelton02.ps, Shelton02.pdf, Shelton02.ps.gz).
# If the extension .abs exists, it will be used as the latex for the abstract
# (eg Shelton02.abs)
#
# The field "WWWtopic" should indicate with which topic the paper should be
# associated.  At the moment, only one topic is allowed per paper.
#
# If desired, the file authors (or a different name if $authorfile is changed)
# lists the URLs for authors whose names appear in the citations.  The file
# consists of a set of URL blocks.  Each one has the format:
# URL
# Author name
# Author name
# ...
# Author name
# <blank line>
# where the blank line separates one block from the next.  All names listed
# after a URL and before the next blank line are assumed to be assocated with
# the URL.
#
# To have the downloadable papers represented by icons, place the icon images
# (which should have been available from the same place as this script) in a
# web accessable directory (and point the $icondir variable at it).
# Example:  For the file Shelton02.ps, the script will look for a file ps.gif
# or ps.jpg in the icon directory and use it.  For the file Shelton02.ps.gz,
# the script will look for ps-gz.gif or ps-gz.jpg.
#
# Once the script is in the right place and the .bib file and papers are in
# the right directory, pointing the web browser at the script should generate
# the page.  If it does not, chances are you do not have the CGI permissions 
# set correctly.  You will have to contact your webmaster to figure out how
# to insure the script is run.
#
#
#
# Example:
# The configuration parameters below assume that the script resides in
# ~/public_html/cgi-bin, the papers reside in ~/public_html/papers/,
# and the bib file is ~/public_html/papers/publications.bib (the authors
# file is ~/public_html/papers/authors and the icons are in
# ~/public_html/icons):
#
# ~/public_html/ -+--- cgi-bin/ ---- papers.cgi
#                 +--- icons/   ---- ps.gif, pdf.gif, etc.
#                 +--- papers/  -+-- publications.bib, authors,
#                                +-- Shelton02.ps, Shelton02.abs, etc.
#
# Then, the web page http://www.example.com/~username/cgi-bin/papers.cgi
# (where www.example.com/~username is replaced by the proper URL base)
# should give the table of papers.


# The configuration information:

# these should be given as relative directories
# (so that urls based on them are correct)
# (no trailing / after directory names)
$paperdbdir = "../papers";
$bibfile = "../papers/publications.bib";
# leave blank to exclude
$authorfile = "../papers/authors";
$webpagetitle = "Publications";
# set to empty string to remove icons
$icondir = "../icons";
# a self-reference relative url
$scriptname = "papers.cgi";

# Changing the appearance of the page requires a bit more perl hacking.
# Go to the proper section (search on):
#  html format:     html output
#  output order:    ordering subs
#  citation format: formatting subs
#
# As written here, it sorts according to topic and reverse chronologically
# within topic (and some other details when there are ties there).  It
# makes one large table with table-wide large-font delimiters before each
# new topic. 
#
# Basically, it loads the whole bibtex file into the hash %recfield
# where $recfield{nn:xx} is the field named xx for the record numbered nn.
# From there is does some sorting and then writes everything out serially.
# It isn't pretty, but it works.  Maybe I'll get around to making it prettier
# sometime.  But I wouldn't hold your breath ;)

# prelim defs:

%mthnum =(jan => 1, january => 1,
	feb => 2, february => 2,
	mar => 3, march => 3,
	apr => 4, april => 4,
	may => 5,
	jun => 6, june => 6,
	jul => 7, july => 7,
	aug => 8, august => 8,
	sep => 9, sept => 9, september => 9,
	oct => 10, october => 10,
	nov => 11, november => 11,
	dec => 12, december => 12);

sub straddset (\@@) {
	my $set = shift;
	my @toadd = @_;
	foreach $a (@toadd) {
		$found = 0;
		foreach $b (@$set) {
			($found=1), last if ($a eq $b);
		}
		push @$set, $a if (!$found);
	}
}

sub strfind ($\@) {
	my $val = shift;
	my $set = shift;
	my $i;
	for($i=0;$i<@$set;$i++) {
		return $i if ($$set[$i] eq $val);
	}
	return -1;
}
	
# formatting subs:

# How to print out a single author
sub processauthor {
	my $au = $_[0];
	if ($au =~ /^([^,]*)\s*,\s*([^,]*)$/) {
		return "$2 $1";
	}
	if ($au =~ /^([^,]*)\s*,\s*([^,]*)\s*,\s*([^,]*)$/) {
		return "$3 $1, $2";
	}
	return $au;
}

# how to take the author line of a bibtex entry and turn it into the
# string to be printed as the author
sub authorformat {
	my @aus = split /\s+and\s+/, $_[0];
	foreach (@aus) {
		$_ = processauthor($_);
	}
	return $aus[0] if (@aus <= 1);
	return "$aus[0] and $aus[1]" if (@aus == 2);
	my $end = pop @aus;
	my $ret = join ', ', @aus;
	$ret .= ", and $end";
	return $ret;
}

sub simplelatex;

# how to take an abstract (the contents of the .abs file if it exists)
# and turn it into html.  Basically, this is simple (and therefore
# not entirely correct) latex->html converter designed to run on the
# simplest of latex that might appear in an abstract.
sub formatabstract {
	foreach (@_) {
		chomp;
		$_ = "<p>" if (!/\S/);
		s/%.*$//g;
	}
	my $oneline = join ' ', @_;
	$oneline =~ s/-+/-/g;
	$oneline =~ s/\$([^\$]*)\^1([^\$]*)\$/$1&sup1;$2/g;
	$oneline =~ s/\$([^\$]*)\^2([^\$]*)\$/$1&sup2;$2/g;
	$oneline =~ s/\$([^\$]*)\^3([^\$]*)\$/$1&sup3;$2/g;
	$oneline =~ s/\$([^\$]*)\$/<i>$1<\/i>/g;
	$oneline =~ s/{\\em\s+(([^{]|\\{)+)}/<em>$1<\/em>/g;
	$oneline =~ s/\\[lc]?dots/.../g;
	$oneline =~ s/\\emph\{([^}]*)\}/<i>$1<\/i>/g;
	$oneline =~ s/\{\\em ([^}]*)\}/<i>$1<\/i>/g;
	# This probably isn't the best way of doing this...
	while($oneline =~ /([^\\])\\(\w+)\s*/) {
		$c2 = uc $2;
		$c1 = $1;
		$oneline =~ s/([^\\])\\(\w+)\s*/$c1$c2/;
	}
	return simplelatex($oneline);
}

sub simplelatex {
	$_ = @_[0];

	s/\\i/i/g;
	s/\\j/j/g;
	s/\\`a/&#224;/g;
	s/\\'a/&#225;/g;
	s/\\^a/&#226;/g;
	s/\\~a/&#227;/g;
	s/\\"a/&#228;/g;
	s/\\`e/&#232;/g;
	s/\\'e/&#233;/g;
	s/\\^e/&#234;/g;
	s/\\"e/&#235;/g;
	s/\\`i/&#236;/g;
	s/\\'i/&#237;/g;
	s/\\^i/&#238;/g;
	s/\\"i/&#239;/g;
	s/\\`o/&#242;/g;
	s/\\'o/&#243;/g;
	s/\\^o/&#244;/g;
	s/\\~o/&#245;/g;
	s/\\"o/&#246;/g;
	s/\\`u/&#249;/g;
	s/\\'u/&#250;/g;
	s/\\^u/&#251;/g;
	s/\\"u/&#252;/g;
	s/\\'y/&#253;/g;
	s/\\"y/&#255;/g;

	s/\\`A/&#192;/g;
	s/\\'A/&#193;/g;
	s/\\^A/&#194;/g;
	s/\\~A/&#195;/g;
	s/\\"A/&#196;/g;
	s/\\`E/&#200;/g;
	s/\\'E/&#201;/g;
	s/\\^E/&#202;/g;
	s/\\"E/&#203;/g;
	s/\\`I/&#204;/g;
	s/\\'I/&#205;/g;
	s/\\^I/&#206;/g;
	s/\\"I/&#207;/g;
	s/\\`O/&#210;/g;
	s/\\'O/&#211;/g;
	s/\\^O/&#212;/g;
	s/\\~O/&#213;/g;
	s/\\"O/&#214;/g;
	s/\\`U/&#217;/g;
	s/\\'U/&#218;/g;
	s/\\^U/&#219;/g;
	s/\\"U/&#220;/g;

	s/\\cC/&#199;/g;
	s/\\cc/&#231;/g;

	s/\\copyright/&#169;/g;
	s/\\pounds/&#163;/g;

	s/~/ /g;

	$_;
}

# how to convert the bibtex record into a latex block
sub blockformat {
	my $i = $_[0];
	my $ret = '';
	$au = simplelatex(authorformat($recfield{"$i:author"}));
	$ed = simplelatex(authorformat($recfield{"$i:editor"}));
	$title = simplelatex($recfield{"$i:title"});
	$book = simplelatex($recfield{"$i:booktitle"});
	$journal = simplelatex($recfield{"$i:journal"});
	$pages = simplelatex($recfield{"$i:pages"});
	$year = simplelatex($recfield{"$i:year"});
	$pages =~ s/--/-/g;
	$volume = simplelatex($recfield{"$i:volume"});
	$number = simplelatex($recfield{"$i:number"});
	$school = simplelatex($recfield{"$i:school"});
	$institution = simplelatex($recfield{"$i:institution"});
	$note = simplelatex($recfield{"$i:note"});
	$note = simplelatex($recfield{"$i:wwwnote"}) if (!$note);
	$type = simplelatex($recfield{"$i:type"});
	$ret .= "$au ($year)";
	$ret .= '. ';
	if ($rectype[$i] eq 'inproceedings') {
		$ret .= "\"<b>$title</b>.\" <i>$book</i>";
		$ret .= " (pp. $pages)" if ($pages);
		$ret .= ".\n";
	} elsif ($rectype[$i] eq 'article') {
		$ret .= "\"<b>$title</b>.\" <i>$journal</i>";
		$ret .= ", $volume" if ($volume);
		$ret .= "($number)" if ($number);
		$ret .= ", $pages" if ($pages);
		$ret .= ".\n";
	} elsif ($rectype[$i] eq 'mastersthesis') {
		$ret .= "<b><i>$title</i></b>. Masters thesis, $school.\n";
	} elsif ($rectype[$i] eq 'phdthesis') {
		$ret .= "<b><i>$title</i></b>. Doctoral dissertation, $school.\n";
	} elsif ($rectype[$i] eq 'techreport') {
		$ret .= "\"<b>$title</b>.\" Technical report. $institution, $type $number.\n";
	} elsif ($rectype[$i] eq 'misc') {
		$ret .= "\"<b>$title</b>.\"\n";
	} elsif ($rectype[$i] eq 'incollection') {
		$ret .= "\"<b>$title</b>.\" In";
		$ret .= " $ed, editors," if ($ed);
		$ret .= " <i>$book</i>" if ($book);
		$ret .= " (pp. $pages)" if ($pages);
		$ret .= ".\n";
	}
	if ($note) {
		$ret .= " $note.\n";
	}
	$ret;
}

# ordering subs

# date sorting: record -> decimal
sub entrydate {
	my $i = $_[0];
	my $year = $recfield{"$i:year"};
	if ($year) {
		my $month = lc $recfield{"$i:month"};
		if ($month =~ /[^0987654321]/) {
			$month = $mthnum{$month};
		}
		if ($month) {
			my $deci = $month*31;
			my $day = $recfield{"$i:day"};
			if ($day) {
				$deci += $day;
			}
			$deci = '0'.$deci while(length($deci)<4);
			$year .= '.'.$deci;
		}
	}
	return $year;
}

# add extra information needed for ordering
sub genordering {
	my $i;
	for($i=0;$i<$recnum;$i++) {
		my $year = entrydate($i);
		my $topic = $recfield{"$i:wwwtopic"};
		if ($topic) {
			$topicorder{$topic} = $year if ($year>$topicorder{$topic});
		}
		my $matchtitle = $recfield{"$i:wwwmatchtitle"};
		if ($matchtitle) {
			$matchtitleorder{$matchtitle} = $year if ($year>$matchtitleorder{$matchtitle});
		}
	}
}

# sort routine for entries
sub entryorder {
	my $ret = ($topicorder{$recfield{"$b:wwwtopic"}} <=> $topicorder{$recfield{"$a:wwwtopic"}});
	return $ret if ($ret);
	my $ret = ($recfield{"$a:wwwtopic"} cmp $recfield{"$b:wwwtopic"});
	return $ret if ($ret);
	$ret = ($matchtitleorder{$recfield{"$b:wwwmatchtitle"}} <=> $matchtitleorder{$recfield{"$a:wwwmatchtitle"}});
	return $ret if ($ret);
	$ret = ($recfield{"$a:wwwmatchtitle"} cmp $recfield{"$b:wwwmatchtitle"});
	return $ret if ($ret);
	$ret = entrydate($b) <=> entrydate($a);
	return $ret if ($ret);
	return $a <=> $b;
}

# ordering for downloadable files
%suffixorder = ("ps" => 3,
                "ps.gz" => 4,
                "pdf" => 1,
                "pdf.gz" => 2);

# sort routine for downloadable files (based on suffixorder, above)
sub filetypeorder {
	my $sa = $suffixorder{$a};
	my $sb = $suffixorder{$b};
	return ($sa <=> $sb) if ($sa && $sb);
	return -1 if ($sa);
	return 1 if ($sb);
	return $a cmp $b;
}

# html output

sub prelist {
	$currenttopic = '';
	$currenttitle = '';
	print "<table cellpadding=5>\n";
}

sub postlist{
	print "</table>\n";
}

sub starttopic {
	my $numw = scalar(@allfiletypes);
	my $ttlw = $numw+2;
	print "<tr><th colspan=$ttlw><font size=+1>$currenttopic</font></th></tr>\n";
	#print "<tr><th>Citation</th><th>bibtex entry</th><th colspan=$numw>file formats</th></tr>\n";
}

sub betweentopics {
	my $numw = scalar(@allfiletypes);
	my $ttlw = $numw+2;
	print "<tr><th colspan=$ttlw><hr></th></tr>\n";
}

# output html for a record
sub printelem {
	my $i = $_[0];
	my $newtopic = $recfield{"$i:wwwtopic"};
	if (($currenttopic ne $newtopic || $currenttopic eq '') && !$singleelem) {
		betweentopics if ($currenttopic);
		$currenttopic = $newtopic;
		$currenttopic = '&nbsp;' if ($currenttopic eq '');
		starttopic;
	}
	print "<tr>\n";

	print "<td>";
	print blockformat($i);
	print "</td>";

	if (!$singleelem) {
		print "<td><a href=\"$scriptname?$recname[$i]\">";
		print "bib";
		print "/abs" if ($hasabstract[$i]);
		print "</a></td>\n";
	}

	my $j;
	for($j=0;$j<@allfiletypes;$j++) {
		my $suf = $allfiletypes[$j];
		if (strfind($suf,@{$filetypes[$i]}) != -1) {
			$fn = $paperdbdir . '/' . $recfield{"$i:wwwfilebase"} . '.' . $suf;
			print "<td><a href=\"$fn\">";
			if ($filetypeicon[$j]) {
				print "<img src=\"$filetypeicon[$j]\" alt=\"$suf\">";
			} else {
				print "$suf";
			}
			print "</a></td>\n";
		} else {
			print "<td>&nbsp;</td>\n";
		}
	}
	print "</tr>\n";
}

sub starthtml {
	print "Content-type:  text/html\n\n";
	print "<html><head><title>$_[0]</title></head>\n<body>\n";
	print "<!-- Generated Automatically using Christian Shelton's Latex-to-HTML script -->\n";
	print "<center><h1>$webpagetitle</h1></center>\n";
}

sub errorexit {
	print "<h1>$_[1]</h1></body></html>\n";
	exit($_[0]);
}

sub endhtml {
	print "</body></html>\n";
}

# Start of "main" program

# start processing
# read bib file:

starthtml($webpagetitle);

if (!open(BIB,$bibfile)) {
	errorexit(1,'Error Processing Database');
}

$recnum = -1;

while(<BIB>) {
	chomp;
	next if (/^\s*%/ || /^\s+$/);
	if (/^\s*@([^{]*)\s*{\s*(\S+)\s*,$/) {
		$one = $1;
		$two = $2;
		if ($recnum>=0 && ($top = $recfield{"$recnum:wwwtopic"})) {
			@topics = split /\s*,\s*/, $top;
			if (@topics>1) {
				$basetype = $rectype[$recnum];
				$basename = $recname[$recnum];
				$recfield{"$recnum:wwwtopic"} = shift @topics;
				foreach (@topics) {
					$recnum++;
					for($i=0;$i<@fields;$i++) {
						$recfield{"$recnum:$fields[$i]"} = $fvalues[$i];
					}
					$recfield{"$recnum:wwwtopic"} = $_;
					$rectype[$recnum] = $basetype;
					$recname[$recnum] = $basename;
				}
			}
		}
		@fields = ();
		@fvalues = ();
		$recnum++;
		$rectype[$recnum] = lc $one;
		$recname[$recnum] = $two;
		$namenum{$two} = $recnum;
	} elsif (/^\s*(\S+)\s*=\s*(.+)$/) {
		$t = $_;
		$f = $1;
		$v = $2;
		$drop = ($f =~ /^WWW/);
		$rectxt[$recnum] .= "$t\n" if (!$drop);
		$f = lc $f;
		$v =~ s/\s+$//;
		if ($v =~ /^"(.*)",$/) {
			$v = $1;
		} elsif ($v =~ /^"(.*)"$/) {
			$v = $1;
		} elsif ($v =~ /^{(.*)},$/) {
			$v = $1;
		} elsif ($v =~ /^{(.*)}$/) {
			$v = $1;
		} elsif ($v =~ /^"(.*[^"])/) {
			$v = $1;
			while(<BIB>) {
				chomp;
				$rectxt[$recnum] .= "$_\n" if (!$drop);
				s/^\s*//;
				s/\s*$//;
				if (/(.*)",$/) {
					$v .= ' ';
					$v .= $1;
					last;
				} elsif (/(.*)"$/) {
					$v .= ' ';
					$v .= $1;
					last;
				}
				$v .= $_;
			}
		} elsif ($v =~ /^{(.*[^}])/) {
			$v = $1;
			while(<BIB>) {
				chomp;
				$rectxt[$recnum] .= "$_\n" if (!$drop);
				s/^\s*//;
				s/\s*$//;
				if (/(.*)},?$/) {
					$v .= ' ';
					$v .= $1;
					last;
				} elsif (/(.*)}$/) {
					$v .= ' ';
					$v .= $1;
					last;
				}
				$v .= $_;
			}
		} elsif ($v =~ /^(\S+),$/) {
			$v = $1;
		}
		$v =~ s/([^\\]|^)[{}]+/$1/g;
		push @fields, $f;
		push @fvalues, $v;
		$recfield{"$recnum:$f"} = $v;
		if ($f eq 'title' && !$recfield{"$recnum:wwwmatchtitle"}) {
			$recfield{"$recnum:wwwmatchtitle"} = $v;
			push @fields, "wwwmatchtitle";
			push @fvalues, $v;
		}
		#$recfield{"$recnum:$f"} = $v;
		#$recfield{"$recnum:wwwmatchtitle"} = $v if ($f eq 'title' && !$recfield{"$recnum:wwwmatchtitle"});
	}
}
close(BIB);
$recnum++;

if (opendir(PD,$paperdbdir)) {
	while($_=readdir(PD)) {
		chomp;
		push @paperfiles, $_;
	}
	closedir(PD);
}

for($i=0;$i<$recnum;$i++) {
	@{$filetypes[$i]} = ();
	if (($stem=$recfield{"$i:wwwfilebase"})) {
		foreach (@paperfiles) {
			if (/$stem\.(.*)$/) {
				$suf = $1;
				if ($suf eq 'abs') {
					$hasabstract[$i] = 1;
				} else {
					straddset(@{$filetypes[$i]},$suf);
					straddset(@allfiletypes,$suf);
				}
			}
		}
	}
}

@allfiletypes = sort filetypeorder @allfiletypes;

if ($icondir) {
	for($i=0;$i<@allfiletypes;$i++) {
		$aft = $allfiletypes[$i];
		$aft =~ s/\./-/g;
		if (-e "$icondir/$aft.gif") {
			$filetypeicon[$i] = "$icondir/$aft.gif";
		} elsif (-e "$icondir/$aft.jpg") {
			$filetypeicon[$i] = "$icondir/$aft.jpg";
		}
	}
}

if ($authorfile && open(AF,$authorfile)) {
	while(<AF>) {
		next if (/^\s*$/);
		$url = $_;
		chomp $url;
		while(<AF>) {
			chomp;
			last if (/^\s*$/);
			$_ = lc $_;
			$authorurl{$_} = $url;
		}
	}
	close(AF);
}

$query = $ENV{QUERY_STRING};
if ($query && ($i=$namenum{$query}) ne '') {
	$title = simplelatex($recfield{"$i:title"});
	$au = simplelatex($recfield{"$i:author"});
	$yr = simplelatex($recfield{"$i:year"});
	@aus = split /\s+and\s+/, $au;
	print "<h2>$title";
	print " ($yr)" if ($yr);
	print "</h2>";
	print "By: ";
	for($j=0;$j<@aus;$j++) {
		print ',' if ($j && @aus>2);
		print ' ' if ($j);
		print 'and ' if ($j==@aus-1 && @aus>1);
		$lcau = lc $aus[$j];
		$printname = processauthor($aus[$j]);
		if ($url=$authorurl{$lcau}) {
			print "<a href=\"$url\">$printname</a>";
		} else {
			print $printname;
		}
	}
	print "<br>\n";
	$stem = $recfield{"$i:wwwfilebase"};
	if ($hasabstract[$i] && open(ABS,"$paperdbdir/$stem.abs")) {
		print "<br><b>Abstract:</b> \n";
		@abs = <ABS>;
		close(ABS);
		print formatabstract(@abs);
	}
	print "<br>\n";
	print "<h2>Download Information</h2>\n";
	$singleelem = 1;
	prelist;
	printelem($i);
	postlist;
	
	print "<h2>Bibtex citation</h2>\n";
	$txt = $rectxt[$i];
	$txt =~ s/\n/<br>\n/g;
	$txt =~ s/\t/&nbsp;&nbsp;&nbsp;/g;
	$txt = '@'."$rectype[$i]\{$query,<br>\n".$txt."\}<br>\n";
	print "<tt>$txt</tt>\n";
	print "<hr><a href=\"$scriptname\">full list</a>\n";
} else {
	genordering;
	for($i=0;$i<$recnum;$i++) {
		push @ordering, $i;
	}
	@ordering = sort entryorder @ordering;

	prelist;
	for($i=0;$i<$recnum;$i++) {
		printelem($ordering[$i]);
	}
	postlist;
}

endhtml();
