(function () {
	var form = $('#loginForm');
	form.on('submit', function (e) {
		e.preventDefault();
		var loginObject = new Object();
		loginObject.password = $("#password").val();
		loginObject.email = $("#email").val();
		$.ajax({
			type: "POST",
			url: "/user/login/",
			data: JSON.stringify(loginObject),
			contentType: "application/json",
			success: function (data, status, xhr) {
				localStorage.setItem("token", data.token);
				window.location.href = "/index/";
			},
			error: function (xhr, errorType) {
				// var modal = $('#demoModal');
				// modal.find('.modal-body').html("Please provide valid email/password");
				// console.log("Error: Data", e.statusText);
				// $('#demoModal').modal('show');
				bootbox.alert({
					message: '<img class="boot-img" src="../static/scf_static/images/error_img.png"><p class="boot-para">Please provide valid email/password<p>',
					size: 'small'
				});
			}
		});
	});
})();

/* logout function */
function logout() {
	$.ajax(
		{
			type: "POST",
			url: "/user/logout/",
			headers: {
				"Authorization": "Token " + localStorage.getItem("token")
			},
			contentType: "application/json",
			success: function (data) {
				window.location.href = "/"
			},
			error: function (xhr, wrrorType) {
				window.location.href = "/"
			}
		});
}