<%inherit file="genaf_base:templates/base.mako" />

<h1>${request.get_resource('genaf.text', None) or "GenAF-base :: Genotyping Analysis Network (base system)"}</h1>

<p>Welcome, user!</p>

<div class="card-deck">

<a class="card" href="/batch">
	<div class="card-body text-center">
		<h4 class="card-title">Manage data</h5>
		<p class="card-text">Browse your data here</p>
	</div>
</a>

<a class="card" href="/analysis">
	<div class="card-body text-center">
		<h4 class="card-title">Analyze data</h5>
		<p class="card-text">Analyze your data here</p>
	</div>
</a>

<a class="card" href="/locus">
	<div class="card-body text-center">
		<h4 class="card-title">Browse locus</h4>
		<p class="card-text">Browse your locus here</p>
	</div>
</a>

<a class="card" href="/panel">
	<div class="card-body text-center">
		<h4 class="card-title">Browse panel</h4>
		<p class="card-text">Browse your panel here</p>
	</div>
</a>

<a class="card" href="#">
	<div class="card-body text-center">
		<h4 class="card-title">Browse docs</h4>
		<p class="card-text">Browse documentation here</p>
	</div>
</a>



</div>

