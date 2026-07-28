const fs = require('fs');
const path = require('path');

const filesToCopy = [
  'index.html',
  'admin_avatar.png',
  's360_logo.png',
  'student_avatar.png',
  'zara_logo.jpg',
  'dataset.csv',
  'final_dataset.csv',
  'student360_dataset.csv',
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
