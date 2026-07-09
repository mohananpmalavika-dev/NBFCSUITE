const { spawnSync } = require('child_process')

const result = spawnSync(process.execPath, [require.resolve('next/dist/bin/next'), 'build'], {
  stdio: 'inherit',
  env: {
    ...process.env,
    NEXT_IGNORE_INCORRECT_LOCKFILE: '1',
  },
})

process.exit(result.status ?? 1)
