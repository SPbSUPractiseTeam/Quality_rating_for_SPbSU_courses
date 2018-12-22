function courseClickHandler() {
    $(".course-statistic-panel").show();
    $(".add-course-panel").hide();
    $(".btn-course").each(function () {
        $(this).removeClass('active');
    });
    $(this).addClass('active');
    let id = $(this).attr('id').split('-')[1];
    parametersChanged({course_id: id});
}

function courseModalDisplayingHandler(event) {
    let operation = event.data.operation;
    let button_link = $(event.relatedTarget).prevAll('a');
    let modal_header = $(`.modal-${operation}_title`);
    modal_header.html(modal_header.html() + " \"" + button_link.text() + "\"");
    $(this).attr(`data-course_to_${operation}`, button_link.attr('id').split('-')[1]);
}


function establishWSConnection() {
    const webSocket = new WebSocket('ws://' + window.location.host +
        '/notifications/');
    const courses_list = document.querySelector(".row-courses-list");
    webSocket.onmessage = function (e) {
        alert(e.data.course_title);
        if (e.data.event = "New Course") {
            var course = document.createElement("div");
            course.innerHTML = `<a id=course-${e.data['course_id']}>${e.data['course_title']}</a>` +
                '<span aria-hidden="true" class="span-delete-course float-right pl-1" data-toggle="modal" data-target="#modalDeleteCourse" title="Удалить курс">🗙</span>\n' +
                '<span aria-hidden="true" class="span-update-course float-right pr-1" data-toggle="modal" data-target="#modalUpdateCourse" title="Изменить название курса">🖉</span>';
            course.classList.add("btn");
            course.classList.add("btn-default");
            course.classList.add("btn-course");
            course.classList.add("py-3");
            course.classList.add("px-2");
            var last_course = courses_list.lastChild;
            courses_list.insertBefore(course, last_course);
        }
    };
    document.ws = webSocket;
}

function deleteCourseLogModalDisplayingHandler() {
    $(this).attr('data-log_to_delete', $(".sel-log").val());
}

function deleteItemClickHandler(event) {
    let item = event.data.item;
    let data = {};
    data[`${item}_id`] = $(this).parents('.modal').attr(`data-${item}_to_delete`);
    $.ajax({
        type: "POST",
        url: `/delete_${item}`,
        data: data,
        success: function () {
            $.cookie(`is_reload_delete_${item}_success`, 'true');
            location.reload();
        },
        error: function () {
            $.cookie(`is_reload_delete_${item}_error`, 'true');
            location.reload();
        }
    });
}

function updateCourseClickHandler() {
    let course_id = $(this).parents('.modal').attr('data-course_to_update');
    $.ajax({
        type: "POST",
        url: "/update_course_title",
        data: {
            'course_id': course_id,
            'title': $('.new_course_title').val()
        },
        success: function () {
            $.cookie('is_reload_update_course_success', 'true');
            $.cookie('current_course_id', course_id);
            location.reload();
        },
        error: function () {
            $.cookie('is_reload_update_course_error', 'true');
            location.reload();
        }
    });
}

function addCourseFormSubmitHandler(event) {
    event.preventDefault();
    let course_title = $('.input-course_title').val();
    let is_course_exists = $(`.btn-course:contains(${course_title})`).length > 0;
    if (!is_course_exists) {
        $.removeCookie('is_reload_upload_course_success');
        $.removeCookie('is_reload_upload_course_error');
        let form_data = new FormData();
        form_data.append('log', $('.form-control-file').prop('files')[0]);
        form_data.append('title', course_title);
        $(".btn-submit-course").hide();
        $(".loader").show();
        $.ajax({
                type: "POST",
                url: "/upload",
                data: form_data,
                processData: false,
                contentType: false,
                success: function () {
                    $.cookie('is_reload_upload_course_success', 'true');
                    location.reload();
                },
                error: function () {
                    $.cookie('is_reload_upload_course_error', 'true');
                    location.reload();
                },
            }
        );
    }
    else {
        $.cookie('is_reload_upload_course_warning', 'true');
        location.reload();
    }
}

function addLogFormSubmitHandler(event) {
    options = event.data.options;
    event.preventDefault();
    let form_data = new FormData();
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
            success: function () {
                $.cookie('is_reload_upload_course_success', 'true');
                location.reload();
            },
            error: function () {
                $.cookie('is_reload_upload_course_error', 'true');
                location.reload();
            },
        }
    );
}

function addCourseClickHandler() {
    $(".course-statistic-panel").hide();
    $(".add-course-panel").show();
    $.ajax({
            type: "POST",
            url: "/upload",
            data: {},
            success: function (data) {
                $('.add-course-panel').html(data);
                $(".loader").hide();
                $('.form-add-course').on("submit", addCourseFormSubmitHandler);
            }
        }
    );
}

function selectChangeHandler(event) {
    let item = event.data.item;
    let params = {};
    params[`${item}_id`] = $(this).val();
    parametersChanged(params);
}

function parametersChanged(options) {
    if (options.course_id === undefined) {
        options.course_id = $("a[id^='course-'][class='active']").attr('id').split('-')[1];
    }
    if (options.log_id === undefined) {
        let current_log = $(".sel-log").val();
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
                let h = $('.row-course-detail').height();
                $(".row-courses-list").height(h);
                $('.form-add-log').on('submit', {options: options}, addLogFormSubmitHandler);
            }
        }
    );
}

function csrfSafeMethod(method) {
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

function makeHandlers() {
    $("a[id|='course']").on("click", courseClickHandler);
    $('#modalDeleteCourse').on('show.bs.modal', {operation: 'delete'}, courseModalDisplayingHandler);
    $('#modalUpdateCourse').on('show.bs.modal', {operation: 'update'}, courseModalDisplayingHandler);
    $('#modalDeleteCourseLog').on('show.bs.modal', deleteCourseLogModalDisplayingHandler);
    $(".btn-delete_course").on("click", {item: 'course'}, deleteItemClickHandler);
    $(".btn-delete_course_log").on("click", {item: 'log'}, deleteItemClickHandler);
    $(".btn-update_course").on("click", updateCourseClickHandler);
    $(".btn-add-course").on("click", addCourseClickHandler);
    $(document).on('change', '.sel-log', {item: 'log'}, selectChangeHandler);
    $(document).on('change', '.sel-module', {item: 'module'}, selectChangeHandler);
}

function showAlertsByCookies() {
    if ($.removeCookie('is_reload_delete_course_success'))
        $(".alert-course-delete-success").show();
    else if (!$.removeCookie('is_reload_upload_course_success') &&
        !$.removeCookie('is_reload_delete_log_success') &&
        !$.removeCookie('is_reload_update_course_success'))
        $.cookie('current_course_id', -1);
    const cookieToAlertDict = {
        'is_reload_delete_course_error': ".alert-course-delete-failure",
        'is_reload_delete_log_error': ".alert-log-delete-failure",
        'is_reload_update_course_error': ".alert-course-update-failure",
        'is_reload_upload_course_error': ".alert-course-upload-failure",
        'is_reload_upload_course_warning': ".alert-course-upload-warning"
    };
    for (let cookie in cookieToAlertDict)
        if ($.removeCookie(cookie))
            $(cookieToAlertDict[cookie]).show();
    if ($.cookie('current_course_id') !== -1)
        $('#course-' + $.cookie('current_course_id')).trigger('click');
}

$(document).ready(function () {
    establishWSConnection();
    makeHandlers();
    $.ajaxSetup({
        beforeSend: function (xhr, settings) {
            let csrf_token = $.cookie('csrftoken');
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
    let h = $(this).height();
    $(".row-courses-list").height(h);
    showAlertsByCookies();
});
