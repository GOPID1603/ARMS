const fs = require('fs');
const path = require('path');

const filesToCopy = [
  'index.html',
  's360_logo.png',
  'student_avatar.png',
  'zara_logo.jpg',
  'dump.json'
];

const destDir = path.join(__dirname, 'build');

if (!fs.existsSync(destDir)) {
  fs.mkdirSync(destDir);
}

filesToCopy.forEach(file => {
  const src = path.join(__dirname, file);
  if (fs.existsSync(src)) {
    fs.copyFileSync(src, path.join(destDir, file));
    console.log(`Copied ${file} to build/`);
  } else {
    console.log(`Warning: File ${file} not found.`);
  }
});

// Write a blank .gitignore to the build folder to clear any inherited ignore rules on gh-pages branch
fs.writeFileSync(path.join(destDir, '.gitignore'), '');
console.log('Created empty .gitignore in build/');
