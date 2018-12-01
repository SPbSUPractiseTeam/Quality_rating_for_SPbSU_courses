$("a[id|='course']").on("click", function () {
    $(".course-statistic-panel").show();
    $(".add-course-panel").hide();
    $(this).addClass('active');
    var id = $(this).attr('id').split('-')[1];
    parameters_changed({course_id: id});
});

$(".bi-pencil").on('click', function () {
    $(this).prev('a').replaceWith()
});

$('#modalDeleteCourse').on('show.bs.modal', function (event) {
    var button = $(event.relatedTarget);
    var button_link = $(event.relatedTarget).prevAll('a');
    var modal_header = $('.modal-delete_title');
    modal_header.html(modal_header.html() + " \"" + button_link.text() + "\"");
    $(this).attr('data-course_to_delete', button_link.attr('id').split('-')[1]);
});

$('#modalUpdateCourse').on('show.bs.modal', function (event) {
    var button = $(event.relatedTarget);
    var button_link = $(event.relatedTarget).prevAll('a');
    var modal_header = $('.modal-update_title');
    modal_header.html(modal_header.html() + " \"" + button_link.text() + "\"");
    $(this).attr('data-course_to_update', button_link.attr('id').split('-')[1]);
});

$('#modalDeleteCourseLog').on('show.bs.modal', function (event) {
    var button = $(event.relatedTarget);
    $(this).attr('data-log_to_delete', $(".sel-log").val());
});

$(".btn-delete_course").on("click", function () {
    $.ajax({
        type: "POST",
        url: "/delete_course",
        data: {
            'course_id': $(this).parents('.modal').attr('data-course_to_delete'),
        },
        success: function (data) {
            $.cookie('is_reload_delete_success', 'true');
            location.reload();
        },
        error: function (data) {
            $.cookie('is_reload_delete_error', 'true');
            location.reload();
        }
    });
});

$(".btn-delete_course_log").on("click", function () {
    $.ajax({
        type: "POST",
        url: "/delete_log",
        data: {
            'log_id': $(this).parents('.modal').attr('data-log_to_delete'),
        },
        success: function (data) {
            $.cookie('is_reload_delete_log_success', 'true');
            location.reload();
        },
        error: function (data) {
            $.cookie('is_reload_delete_log_error', 'true');
            location.reload();
        }
    });
});

$(".btn-update_course").on("click", function () {
    var course_id = $(this).parents('.modal').attr('data-course_to_update');
    $.ajax({
        type: "POST",
        url: "/update_course_title",
        data: {
            'course_id': course_id,
            'title': $('.new_course_title').val()
        },
        success: function (data) {
            $.cookie('current_course_id', course_id);
            location.reload();
        },
        error: function (data) {
            $.cookie('is_reload_update_error', 'true');
            location.reload();
        }
    });
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
                            $.removeCookie('is_reload_upload_success');
                            $.removeCookie('is_reload_upload_error');
                            $.cookie('is_reload_upload_warning', 'true');
                            is_course_exists = true;
                        }
                    });
                    if (!is_course_exists) {
                        var form_data = new FormData();

                        form_data.append('log', $('.form-control-file').prop('files')[0]);
                        form_data.append('title', $('.input-course_title').val());
                        $(".btn-submit-course").hide();
                        $(".loader").show();
                        $.ajax({
                                type: "POST",
                                url: "/upload",
                                data: form_data,
                                processData: false,
                                contentType: false,
                                success: function (data) {
                                    $.cookie('is_reload_upload_success', 'true');
                                    $(location).attr("href", '/');
                                },
                                error: function (jqXHR, textStatus, errorThrown) {
                                    $.cookie('is_reload_upload_error', 'true');
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
        options.course_id = $("a[id^='course-'][class='active']").attr('id').split('-')[1];
    }
    if (options.log_id === undefined) {
        current_log = $(".sel-log").val();
        if (current_log !== undefined)
            options.log_id = current_log;
        else
            options.log_id = -1;
    }
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
                $("a[id='[course-" + options.course_id + "]'").addClass('active');
                var h = $('.row-course-detail').height();
                $(".row-courses-list").height(h);
                $('.form-add-log').on('submit', function (event) {
                    event.preventDefault();
                    var form_data = new FormData();
                    form_data.append('log', $('.form-control-file').prop('files')[0]);
                    form_data.append('title', $("a[id^='course-'][class='active']").text());
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
                                $.cookie('is_reload_upload_success', 'true');
                                location.reload();
                            },
                            error: function (jqXHR, textStatus, errorThrown) {
                                $.cookie('is_reload_upload_error', 'true');
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
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            var csrf_token = $.cookie('csrftoken');
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrf_token);
            }
        }
    });
    if ($(".is-already-authenticated").length) {
        setTimeout(function () {
            $(location).attr("href", '/');
        }, 1000);
    }
    var h = $(this).height();
    $(".row-courses-list").height(h);
    if ($.removeCookie('is_reload_delete_success'))
        $(".alert-course-delete-success").show();
    else if (!$.removeCookie('is_reload_upload_success') && !$.removeCookie('is_reload_delete_log_success'))
        $.cookie('current_course_id', -1);
    if ($.removeCookie('is_reload_delete_error'))
        $(".alert-course-delete-failure").show();
    if ($.removeCookie('is_reload_delete_log_error'))
        $(".alert-log-delete-failure").show();
    if ($.removeCookie('is_reload_update_error'))
        $(".alert-course-update-failure").show();
    if ($.removeCookie('is_reload_upload_error'))
        $(".alert-course-upload-failure").show();
    if ($.removeCookie('is_reload_upload_warning'))
        $(".alert-course-upload-warning").show();
    if ($.cookie('current_course_id') !== -1) {
        $('#course-' + $.cookie('current_course_id')).trigger('click');
    }
});
