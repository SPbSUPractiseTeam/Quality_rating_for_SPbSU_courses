$("button[id|='course']").on("click", function () {
    $(".course-statistic-panel").show();
    $(".add-course-panel").hide();
    $(this).addClass('active');
    var id = $(this).attr('id').split('-')[1];
    parameters_changed({course_id: id});
});

$(".btn-add-course").on("click", function () {
    $(".course-statistic-panel").hide();
    $(".add-course-panel").show();
    $.ajax({
            type: "POST",
            url: "/upload",
            data: {},
            success: function (data) {
                $('.add-course-panel').html(data);
                $(".loader").hide();
                $('.form-add-course').on("submit", function (event) {
                    event.preventDefault();
                    var is_course_exists = false;
                    $(".btn-course").each(function () {
                        if ($(this).text() === $('.form-control').val()) {
                            $.removeCookie('is_reload_error');
                            $.removeCookie('is_reload_success');
                            $.cookie('is_reload_warning', 'true');
                            is_course_exists = true;
                        }
                    });
                    if (!is_course_exists) {
                        var form_data = new FormData();
                        form_data.append('log', $('.form-control-file').prop('files')[0]);
                        form_data.append('title', $('.form-control').val());
                        $(".btn-submit-course").hide();
                        $(".loader").show();
                        $.ajax({
                                type: "POST",
                                url: "/upload",
                                data: form_data,
                                processData: false,
                                contentType: false,
                                success: function (data) {
                                    $.cookie('is_reload_success', 'true');
                                    location.reload();
                                },
                                error: function (jqXHR, textStatus, errorThrown) {
                                    $.cookie('is_reload_error', 'true');
                                    location.reload();
                                },
                            }
                        );
                    }
                    else
                        location.reload();
                });
            }
        }
    );
});

$(document).on('change', '.sel-module', function () {
    var id = $(this).val();
    parameters_changed({module_id: id});
});

$(document).on('change', '.sel-log', function () {
    var id = $(this).val();
    parameters_changed({log_id: id});
});

function parameters_changed(options) {
    if (options.course_id === undefined) {
        options.course_id = $(".btn-course.active").attr('id').split('-')[1];
    }
    if (options.log_id === undefined)
        options.log_id = -1;
    if (options.module_id === undefined)
        options.module_id = -1;
    $.ajax({
            type: "POST",
            url: "/detail",
            data: {
                course_id: options.course_id,
                log_id: options.log_id,
                module_id: options.module_id,
            },
            success: function (data) {
                $('.course-statistic-panel').html(data);
                $(".loader_little").hide();
                if (options.log_id !== -1)
                    $('.sel-log').val(options.log_id);
                if (options.module_id !== -1)
                    $('.sel-module').val(options.module_id);
                $("button[id='[course-" + options.course_id + "]'").addClass('active');
                var h = $('.row-course-detail').height();
                $(".row-courses-list").height(h);
                $('.form-add-log').on('submit', function (event) {
                    event.preventDefault();
                    var form_data = new FormData();
                    form_data.append('log', $('.form-control-file').prop('files')[0]);
                    form_data.append('title', $('.btn-course.active').text());
                    form_data.append('course_id', options.course_id);
                    form_data.append('log_id', options.log_id);
                    form_data.append('module_id', options.module_id);
                    $(".btn-submit-course").hide();
                    $(".loader_little").show();
                    $.ajax({
                            type: "POST",
                            url: "/detail",
                            data: form_data,
                            processData: false,
                            contentType: false,
                            success: function (data) {
                                $.cookie('is_reload_success', 'true');
                                location.reload();
                            },
                            error: function (jqXHR, textStatus, errorThrown) {
                                $.cookie('is_reload_error', 'true');
                                location.reload();
                            },
                        }
                    );
                });
            }
        }
    );
}

function csrfSafeMethod(method) {
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

$(document).ready(function () {
    if ($(".is-already-authenticated").length){
        setTimeout(function () {
           $( location ).attr("href", '/');
        }, 100000);
    }
    var h = $(this).height();
    $(".row-courses-list").height(h);
    if (!$.removeCookie('is_reload_success'))
        $(".alert-course-upload-success").hide();
    else {
        setTimeout(function () {
            $(".alert-course-upload-success").hide('slow');
        }, 4000);
    }
    if (!$.removeCookie('is_reload_error'))
        $(".alert-course-upload-failure").hide();
    else {
        setTimeout(function () {
            $(".alert-course-upload-failure").hide('slow');
        }, 4000);
    }
    if (!$.removeCookie('is_reload_warning'))
        $(".alert-course-upload-warning").hide();
    else {
        setTimeout(function () {
            $(".alert-course-upload-warning").hide('slow');
        }, 4000);
    }
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            var csrf_token = $.cookie('csrftoken');
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrf_token);
            }
        }
    });
});
