
from rhombus.lib.helpers import *
from rhombus.lib.tags import li, ul, a, div

def render_browse_menu(request):
	return create_nav_menu( 'Browse', '/browse',
		[
			('Batch', '/batch'),
			('Locus', '/locus'),
			('Panel', '/panel'),	
		],
		request
	)


def render_analyze_menu(request):
	return create_nav_menu("Analyze", "/browse",
		[
			("Allele Frequency", "/tools/allele"),
			("Haplotype Analysis", "/tools/haplotype"),
			("PCA/PCoA", "/tools/pca"),
		],
		request
	)


def render_utility_menu(request):
	pass

def create_nav_menu(label, href, dropdowns, request):
	menu = li(a(label, href=href, class_="nav-link dropdown-toggle",
						**{"data-toggle": "dropdown"}),
				 class_="nav-item dropdown")[
				div(class_="dropdown-menu").add(
					* list(
						a(dd_label, href=dd_href, class_="dropdown-item") 
							for (dd_label, dd_href) in dropdowns
					)
				)
		]
	return menu
