function formatDateTime(timeStamp) {
    /*时间戳转换为时间*/
    var date = new Date();
    date.setTime(timeStamp * 1000);
    var y = date.getFullYear();
    var m = date.getMonth() + 1;
    m = m < 10 ? ('0' + m) : m;
    var d = date.getDate();
    d = d < 10 ? ('0' + d) : d;
    var h = date.getHours();
    h = h < 10 ? ('0' + h) : h;
    var minute = date.getMinutes();
    var second = date.getSeconds();
    minute = minute < 10 ? ('0' + minute) : minute;
    second = second < 10 ? ('0' + second) : second;
    return y + '-' + m + '-' + d + ' ' + h + ':' + minute + ':' + second;
}


/**
 * 将秒数换成时分秒格式
 */
function formatSeconds(value) {
    var secondTime = parseInt(value);// 秒
    var minuteTime = 0;// 分
    var hourTime = 0;// 小时
    if (secondTime > 60) {//如果秒数大于60，将秒数转换成整数
        //获取分钟，除以60取整数，得到整数分钟
        minuteTime = parseInt(secondTime / 60);
        //获取秒数，秒数取佘，得到整数秒数
        secondTime = parseInt(secondTime % 60);
        //如果分钟大于60，将分钟转换成小时
        if (minuteTime > 60) {
            //获取小时，获取分钟除以60，得到整数小时
            hourTime = parseInt(minuteTime / 60);
            //获取小时后取佘的分，获取分钟除以60取佘的分
            minuteTime = parseInt(minuteTime % 60);
        }
    }
    var result = "" + parseInt(secondTime) + "秒";

    if (minuteTime > 0) {
        result = "" + parseInt(minuteTime) + "分" + result;
    }
    if (hourTime > 0) {
        result = "" + parseInt(hourTime) + "小时" + result;
    }
    return result;
}


/**
 * [Queue]
 * @param {[Int]} size [队列大小]
 */
function Queue(size) {
    var list = [];

    //向队列中添加数据
    this.push = function (data) {
        if (list.length >= size) {
            list.shift()
        }
        list.push(data)
    };

    //从队列中取出数据
    this.pop = function () {
        return list.pop();
    };

    //返回队列的大小
    this.size = function () {
        return list.length;
    };

    //返回队列的内容
    this.quene = function () {
        return list;
    }
}

/*IP正则表达式*/
var ip_pattern = /^(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])\.(\d{1,2}|1\d\d|2[0-4]\d|25[0-5])$/;

function isValidIp(ip_value) {
    return ip_pattern.test(ip_value);
}


function operate_type() {

    if ($("#oprate_type").val() == "Frp模式") {
        if (!$("#park_name").val() || !$("#ip_list").val()) {
            bootbox.alert({
                title: "提示信息",
                message: "请输入有效车场名称并选择一个终端IP！",
                size: "small"
            });
            return
        }

        var param = {
            park_name: $("#park_name").val(),
            current_ip: $("#ip_list").val()
        };

    } else {
        if (!isValidIp($("#arm_address").val())) {
            bootbox.alert({
                title: "提示信息",
                message: "请输入有效IP地址！",
                size: "small"
            });
            return
        }

        var param = {
            hostname: $("#arm_address").val(),
            port: $("#arm_port").val()
        };
    }

    return param
}


function operate_type_no_ip_list() {

    if ($("#oprate_type").val() == "Frp模式") {
        if (!$("#park_name").val()) {
            bootbox.alert({
                title: "提示信息",
                message: "请输入有效车场名称！",
                size: "small"
            });
            return
        }

        var param = {
            park_name: $("#park_name").val()
        };

    } else {
        if (!isValidIp($("#arm_address").val()) || !$("#arm_port").val()) {
            bootbox.alert({
                title: "提示信息",
                message: "请输入有效IP地址和端口号！",
                size: "small"
            });
            return
        }

        var param = {
            hostname: $("#arm_address").val(),
            port: $("#arm_port").val()
        };
    }

    return param
}