const { replaceInFile } = require('replace-in-file');

const options = {
    files: 'path/to/your/file.html',
    from: [
        /https:\/\/userapp\.zyrosite\.com\/1727788381\/assets\/js\/index-DmoyKSTs\.js/g,
        /https:\/\/userapp\.zyrosite\.com\/1727788381\/assets\/css\/index-DY2-gzvD\.css/g
    ],
    to: [
        'assets/js/index.js',
        'assets/css/styles.css'
    ],
};

async function replaceFiles() {
    try {
        const results = await replaceInFile(options);
        console.log('Replacement results:', results);
    } catch (error) {
        console.error('Error occurred:', error);
    }
}

replaceFiles();