## -*- coding: utf-8 -*-
% if request and request.is_xhr:
  ${next.body()}

  <script type="text/javascript">
    //<![CDATA[
    ${self.jscode()}
    //]]>
  </script>

% else:
<!DOCTYPE html>
<html lang="en">
  <!-- genaf_base:templates/base.mako -->
  <head>
  <meta charset="utf-8">
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>${request.get_resource('genaf.title', None) or "GenAF-Base"}</title>

  <!-- styles -->
  <!--
  <link href="${request.static_url('rhombus:static/bootstrap-4/css/bootstrap.min.css')}" rel="stylesheet" />
-->
  <link href="/assets/rb/bootstrap-4.4.1-dist/css/bootstrap.min.css" rel="stylesheet" />
  <link href="/assets/rb/fontawesome-free-5.12.1-web/css/all.min.css" rel="stylesheet" />
  <link href="${request.static_url('rhombus:static/fonts/source-sans-pro.css')}" rel="stylesheet" />

  <!--
  <link href="${request.static_url('rhombus:static/font-awesome-4.5.0/css/font-awesome.min.css')}" rel="stylesheet" />
-->
  <link href="${request.static_url('rhombus:static/select2/css/select2.min.css')}" rel="stylesheet" />
  <link href="${request.static_url('rhombus:static/select2/css/select2-bootstrap.min.css')}" rel="stylesheet" />
  <link href="${request.static_url('rhombus:static/css/custom.css')}" rel="stylesheet" />

  <link href="${request.static_url('rhombus:static/rst/rst.css')}" rel="stylesheet" />
  <link href="${request.static_url('rhombus:static/rst/theme.css')}" rel="stylesheet" />

  <link href="${request.static_url('genaf_base:static/custom.css')}" rel="stylesheet" />


  ${self.stylelink()}

  </head>
  <body>

    <!-- Static navbar -->
	<%include file="includes/topline.mako" args="user_menu='abc'" />

    <div class="container-fluid">
      <div class="row"><div class="col-md-12">
      ${flash_msg()}
      </div></div>
      
      <div class="row">

        <div class="col-md-12">

        ${next.body()}

        </div>

      </div>

    </div>
    <footer>
    <div class="container-fluid">
      <div class='row'>
      <div class='col-md-12'>
        <!-- font: Nobile -->
        <p>(C) 2020 Eijkman Institute for Molecular Biology, Indonesia <br>
           (C) 2020 Menzies School of Health Research, Australia</p>
      </div>
      </div>
    </div>
    </footer>

    <br><br><br>

% if stickybar:
${stickybar}
<!--
    <nav class="navbar fixed-bottom navbar-expand-sm navbar-light toolbar">
      <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarCollapse" aria-controls="navbarCollapse" aria-expanded="false" aria-label="Toggle navigation">
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse" id="navbarCollapse">
        <span class="navbar-text">[Node ID: 12]</span>
        <ul class="navbar-nav mr-auto">
          <li class="nav-item active">
            <a class="nav-link" href="#">Home <span class="sr-only">(current)</span></a>
          </li>
          <li class="nav-item">
            <a class="nav-link" href="#">Link</a>
          </li>
          <li class="nav-item">
            <a class="nav-link disabled" href="#">Disabled</a>
          </li>
        </ul>
        <ul class="navbar-nav">
          <li class="nav-item dropup">
            <a class="nav-link dropdown-toggle" href="https://getbootstrap.com" id="dropdown10" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">Dropup</a>
            <div class="dropdown-menu dropdown-menu-right" aria-labelledby="dropdown10">
              <a class="dropdown-item" href="#">Action</a>
              <a class="dropdown-item" href="#">Another action</a>
              <a class="dropdown-item" href="#">Something else here</a>
            </div>
          </li>
        </ul>
      </div>
    </nav>
-->
% endif

<!-- self.scriptlinks() -->
${self.scriptlinks()}
<!-- /self.scriptlinks() -->

  </body>

</html>
% endif
##
##
<%def name="stylelink()">
</%def>
##
##
<%def name="scriptlinks()">

<!--
    <script src="${request.static_url('rhombus:static/bootstrap-4/js/jquery-3.3.1.min.js')}"></script>
    <script src="${request.static_url('rhombus:static/bootstrap-4/js/bootstrap.bundle.min.js')}"></script>
    -->

    <script src="/assets/rb/jquery-3.4.1.min.js"></script>
    <script src="/assets/rb/popper.min.js"></script>
    <script src="/assets/rb/bootstrap-4.4.1-dist/js/bootstrap.bundle.min.js"></script>
    <script src="${request.static_url('rhombus:static/select2/js/select2.min.js')}"></script>

    ${self.jslink()}
    <script type="text/javascript">
        //<![CDATA[
        ${self.jscode()}
        //]]>
    </script>
</%def>
##
##
<%def name='flash_msg()'>
<!-- flash message container -->
% if request.session.peek_flash():

  % for msg_type, msg_text in request.session.pop_flash():
   <div class="alert alert-${msg_type} alert-dismissible fade show" role="alert">
     ${msg_text}
     <button type="button" class="close" data-dismiss="alert" aria-label="Close">
       <span aria-hidden="true">&times;</span>
     </button>
   </div>
  % endfor

% endif
</%def>

##
<%def name='jscode()'>
${ code or '' | n }
</%def>

##
<%def name="jslink()">
<!-- cmsfix:templates/base.mako jslink() -->
${ codelink or '' | n }
</%def>
