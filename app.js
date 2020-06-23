
const fs = require('fs');
const Py_to_Js = require('./Py_to_Js');

const info = (imageUrl) => {
    return {
        // python脚本
        file: 'image_analysis.py',
        // 待处理图片地址
        imageUrl: imageUrl
    }
};


const zlUrl = encodeURI('./img/test1.png');


Py_to_Js(info(zlUrl), function (result) {
    console.log(result)

})