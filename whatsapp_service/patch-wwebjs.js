const fs = require('fs');
const path = require('path');

const file = path.join(
    __dirname, 'node_modules', 'whatsapp-web.js',
    'src', 'util', 'Injected', 'Utils.js'
);

if (!fs.existsSync(file)) {
    console.error('❌ Utils.js nahi mili:', file);
    process.exit(1);
}

let src = fs.readFileSync(file, 'utf8');

if (src.includes('delete message.__x_id')) {
    console.log('✅ Already patched');
    process.exit(0);
}

// message object banne ke turant baad wali jagah dhundo
const anchors = [
    /^([ \t]*)\/\/ Bot's won't reply if canonicalUrl is set \(linking\)/m,
    /^([ \t]*)if \(botOptions\) \{\s*\r?\n\s*delete message\.canonicalUrl;/m,
];

const anchor = anchors.find((re) => re.test(src));

if (!anchor) {
    console.error('❌ Anchor nahi mila. Utils.js ka sendMessage wala hissa bhejo.');
    process.exit(1);
}

src = src.replace(
    anchor,
    (match, indent) => `${indent}delete message.__x_id; // patch: media __x_id collision fix\n\n${match}`
);

fs.writeFileSync(file, src);
console.log('✅ Patch applied');