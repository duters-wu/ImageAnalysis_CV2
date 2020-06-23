
/**
 * 与python脚本通信，进行一个请求
 * @param {object} info：与python脚本通信的配置
 * @param {function} callback：通信完成后执行的事件，传递参数为返回的数据 
 */

const childProcess = require('child_process');


function Py_to_Js(info, callback) {
    /* 发送请求 */
    return new Promise((resolve, reject) => {
        // cmd
        const cps = childProcess.spawn('python', [
            // avgs
            info.file,
            info.imageUrl
        ]);
        // 储存分析信息
        let result = {};

        // 错误
        cps.stderr.on('data', function (data) {
            reject(Buffer.from(JSON.parse(JSON.stringify(data))).toString());
        });

        // 获取数据
        cps.stdout.on('data', function (data) {
            result = data;
        });

        // 获取完数据
        cps.on('exit', function (code) {
            resolve(JSON.parse(Buffer.from(JSON.parse(JSON.stringify(result))).toString()));
        });

    }).then(callback).catch((error) => {
        console.log(error);
    });
}

module.exports = Py_to_Js;

