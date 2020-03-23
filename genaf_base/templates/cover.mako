<!DOCTYPE html>
<html lang="en">
<head>
	<title>${request.get_resource('genaf.title', None) or "GenAF-Base"}</title>
	<meta charset="UTF-8">
	<meta name="viewport" content="width=device-width, initial-scale=1">
<!--===============================================================================================-->	
	<link rel="icon" type="image/png" href="/assets/gb/images/icons/favicon.ico"/>
<!--===============================================================================================-->
  <link href="/assets/rb/bootstrap-4.4.1-dist/css/bootstrap.min.css" rel="stylesheet" />
  <link href="/assets/rb/fontawesome-free-5.12.1-web/css/all.min.css" rel="stylesheet" />
<!--===============================================================================================-->
	<link rel="stylesheet" type="text/css" href="/assets/gb/css/util.css">
	<link rel="stylesheet" type="text/css" href="/assets/gb/css/main.css">
<!--===============================================================================================-->
</head>
<body style="background-color: #666666;">
	
	<div class="limiter">
		<div class="container-login100">
			<div class="wrap-login100">
				<form class="login100-form validate-form" action="/login" method="POST">
					<span class="login100-form-title p-b-43">
						Login to continue
					</span>
					
					
					<div class="wrap-input100 validate-input" data-validate = "Valid username is required">
						<input class="input100" type="text" name="login">
						<span class="focus-input100"></span>
						<span class="label-input100">Login</span>
					</div>
					
					
					<div class="wrap-input100 validate-input" data-validate="Password is required">
						<input class="input100" type="password" name="password">
						<span class="focus-input100"></span>
						<span class="label-input100">Password</span>
					</div>

					<div class="flex-sb-m w-full p-t-3 p-b-32">
						<div class="contact100-form-checkbox">
							<input class="input-checkbox100" id="ckb1" type="checkbox" name="remember-me">
							<label class="label-checkbox100" for="ckb1">
								Remember me
							</label>
						</div>

						<div>
							<a href="#" class="txt1">
								Forgot Password?
							</a>
						</div>
					</div>
			

					<div class="container-login100-form-btn">
						<button class="login100-form-btn">
							Login
						</button>
					</div>
					
					<div class="text-center p-t-46 p-b-20">
						<span class="txt2">
							or
						</span>
					</div>

					<div class="container-login100-form-btn">
						<button class="login100-form-btn">
							Login as Guest
						</button>
					</div>

				</form>

				<div class="login100-more" style="background-image: url('/assets/gb/images/banner1.jpg');">
					<h1>vivaxGEN-SNP (beta version)</h1>
					<h3>a SNP-based genotyping platform for <i>Plasmodium vivax</i></h3>
				</div>
			</div>
		</div>
	</div>
	
	<script src="/assets/rb/jquery-3.4.1.min.js"></script>
    <script src="/assets/rb/popper.min.js"></script>
    <script src="/assets/rb/bootstrap-4.4.1-dist/js/bootstrap.bundle.min.js"></script>

<!--===============================================================================================-->
	<script src="/assets/gb/js/main.js"></script>

</body>
</html>