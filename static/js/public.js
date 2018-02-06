/* ******************************************************************************************
************************            加tab页的div容器        *********************************
*******************************************************************************************/
;(function(defaults, $, window, document, undefined) {

	'use strict';

	$.extend({
		// Function to change the default properties of the plugin
		// Usage:
		// jQuery.tabifySetup({property:'Custom value'});
		tabifySetup : function(options) {

			return $.extend(defaults, options);
		}
	}).fn.extend({
		// Usage:
		// jQuery(selector).tabify({property:'value'});
		tabify : function(options) {

			options = $.extend({}, defaults, options);

			return $(this).each(function() {
        var $element, tabHTML, $tabs, $sections;

        $element = $(this);
        $sections = $element.children();

        // Build tabHTML
        tabHTML = '<ul class="tab-nav">';
        $sections.each(function() {
          if ($(this).attr("title") && $(this).attr("id")) {
            tabHTML += '<li><a href="#' + $(this).attr("id") + '" id="'+ $(this).attr("id") +'">' + $(this).attr("title") + '</a></li>';
          }
        });
        tabHTML += '</ul>';

        // Prepend navigation
        $element.prepend(tabHTML);

        // Load tabs
        $tabs = $element.find('.tab-nav li');

        // Functions
        var activateTab = function(id) {
          $tabs.filter('.active').removeClass('active');
          $sections.filter('.active').removeClass('active');
          $tabs.has('a[href="' + id + '"]').addClass('active');
          $sections.filter(id).addClass('active');
        }

        // Setup events
        $tabs.on('click', function(e){
          activateTab($(this).find('a').attr('href'));
          e.preventDefault();
        });

        // Activate first tab
        activateTab($tabs.first().find('a').attr('href'));

			});
		}
	});
})({
	property : "value",
	otherProperty : "value"
}, jQuery, window, document);

/* *
 * str时间转为UTC时间
 * 传入参数：
 * 1. string串
 * 返回值：UTC格式时间
 *
 * */
function str2UTC(str) {
    date = new Date(Date.parse(str.replace(/-/g, "/")));
    //组成UTC
    var y =  date.getUTCFullYear();
    var m = date.getUTCMonth() ;
    var d = date.getUTCDate();
    var h= date.getUTCHours();
    var M = date.getUTCMinutes();
    var s = date.getUTCSeconds();
    //这里只选年月日，如有需要可以多选
    var utc = Date.UTC(y,m,d);
    return utc
};

//obj为标签栏id(格式$("#se"))，codetype为sys_code中code类型的名称
function selectInit(obj,codeType) {
    //初始下拉框
    var url = '/publicMethod/getSYSCode';
    $.ajax({
        type: 'POST',
        data:{
            "codeType":codeType,
        },
        dataType: 'json',
        url: url,
        success: function (data) {
            data = JSON.parse(data);
            //根据data返回值初始化下拉框
            for(var i=0;i<data.length;i++){
                var opt=$("<option>");
                opt.val(data[i].val);
                opt.text(data[i].text);
                obj.append(opt);
            }
        },
        error: errorInfo,
        //采用异步
        async: false
    });
};

/*
* 获取数据库键值的方法
* 输入参数：codetype为sys_code中code类型的名称
* 返回参数：
* */
function getCode(codeType) {
    //初始下拉框
    var url = '/publicMethod/getSYSCode';
    var codeData = []
    $.ajax({
        type: 'POST',
        data:{
            "codeType":codeType,
        },
        dataType: 'json',
        url: url,
        success: function (data) {
            data = JSON.parse(data);
            for(var i=0;i<data.length;i++){
                var code = {}
                code['val'] = data[i].val;
                code['text'] = data[i].text;
                codeData.push(code);
            }
        },
        error: errorInfo,
        //是否采用异步，false表示同步
        async: false
    });
    return codeData;
};

//错误信息处理界面
var errorInfo = function(msg){
    console.log(msg);
    //关闭进度条
    //$('body').mLoading("hide");
};

/*
* 更改内容渐变字体
* 传入参数：
* 1. id HTML tag id
* 2. text需要更新的字体
* 3. fontColor 字体的颜色
* 无返回值
* */
function changeFont(id, text, fontColor) {
    //如果字段值有变化，触发修改动作
    if ($("#" + id).text() != text) {
        $("#" + id).animate({opacity: '0'}, 500, function () {
            $(this).html(text).css("color", fontColor);
        }).animate({opacity: '1'}, 500);
    }
};

/*
* 字典排序
* 传入参数：
* 1. 字典  {x:2,z:1,y:3}
* 无返回值
* 1. 字典  {x:2，y:3，z:1}
* */
function dictSort(dict) {
    var sdic=Object.keys(dict).sort();
    var newDict = {}
    debugger;
    for(ki in sdic){
        newDict[sdic[ki]] = dict[sdic[ki]];
    }
    return newDict;
}