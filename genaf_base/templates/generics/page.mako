<%inherit file="genaf_base:templates/base.mako" />

% if html:
${ html }
% else:
${ content | n }
% endif

##
