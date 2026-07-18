# Authentication profile commands
mod auth 'commands/auth.just'

# Configuration access commands
mod config 'commands/config.just'

# Local development commands
mod dev 'commands/dev.just'

# Repository maintenance commands
mod repo 'commands/repo.just'

# Environment synchronization commands
mod sync 'commands/sync.just'

[private]
default:
    @just --list
