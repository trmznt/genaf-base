<%inherit file="genaf_base:templates/base.mako" />

<h2>Samples</h2>

<form class='form-inline' method='get'>
  <input type='text' id='q' name='q' value='${request.params.get("q","")}' class='input-xlarge' placeholder='Please provide query here' />
  <button type='submit' cls='btn'>Filter</button>
</form>

${ html }

##
##  START OF METHODS
##
<%def name="stylelink()">
  <link href="${request.static_url('rhombus:static/datatables/datatables.min.css')}" rel="stylesheet" />  
</%def>
##
##
<%def name="jslink()">
<script src="${request.static_url('rhombus:static/datatables/datatables.min.js')}"></script>
</%def>
##
##
<%def name="jscode()">
${ code | n }
</%def>
##





