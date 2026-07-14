module.exports = {
  apps: [
    {
      name: 'adam-frontend',
      script: 'npm',
      args: 'run dev',
      cwd: '/home/user/webapp/frontend',
      env: { NODE_ENV: 'development', PORT: 3000 },
      watch: false,
      instances: 1,
      exec_mode: 'fork',
    },
  ],
}
