
<nav class="navbar navbar-expand-md navbar-dark bg-dark mb-4">
	<a class="navbar-brand" href="/">${request.get_resource('genaf.title', 'GenAF')}</a>
    <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarCollapse" aria-controls="navbarCollapse" aria-expanded="false" aria-label="Toggle navigation">
    	<span class="navbar-toggler-icon"></span>
    </button>
    <div class="collapse navbar-collapse justify-content-stretch" id="navbarCollapse">
        <div class="navbar-nav mr-auto">
        ${h.render_browse_menu(request)}
        ${h.render_analyze_menu(request)}
        </div>
        <div class="navbar-nav justify-content-stretch">
    	${user_menu(request)}
        </div>
    </div>
</nav>
