fs = require('fs');

// convert the .json file that python created into a list that this script can use
module.exports = function parseJsonFile(filename) {
    var content = fs.read(filename + ".json");
    return JSON.parse(content);
}
