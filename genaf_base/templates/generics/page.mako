<%inherit file="genaf_base:templates/base.mako" />

% if html:
${ html }
% elif content:
${ content | n }
% else:
<p>No HTML nor content</p>
% endif

##
