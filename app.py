def cleanup_old_sessions(base_temp_dir="/tmp", max_age_hours=24, empty_age_minutes=5):
    """
    Two-tier cleanup strategy with session protection:
    1. Delete EMPTY folders older than empty_age_minutes (default 5 min)
    2. Delete ANY folder older than max_age_hours (default 24 hours)
    
    CRITICAL: Never delete the current session's temp directory!
    
    Args:
        base_temp_dir: Base directory to scan (default /tmp)
        max_age_hours: Max age for any folder before deletion (default 24)
        empty_age_minutes: Max age for empty folders before deletion (default 5)
    """
    lock_file = None
    try:
        # Try to acquire an exclusive lock with non-blocking mode
        lock_file = open(CLEANUP_LOCK_FILE, 'w')
        fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        
        # Successfully acquired lock - this session will do the cleanup
        print(f"✓ Acquired cleanup lock, starting cleanup...")
        
        # Get current session's temp directory to protect it
        current_temp_dir = st.session_state.get("temp_dir", None)
        
        temp_path = Path(base_temp_dir)
        cutoff_time = time.time() - (max_age_hours * 3600)
        empty_cutoff_time = time.time() - (empty_age_minutes * 60)
        
        cleaned_count = 0
        skipped_current = 0
        skipped_active = 0
        skipped_unparseable = 0
        
        # Find all wenokn_* directories
        for temp_dir in temp_path.glob("wenokn_*"):
            if temp_dir.is_dir():
                try:
                    # CRITICAL: Skip current session's temp directory
                    if current_temp_dir and str(temp_dir) == current_temp_dir:
                        skipped_current += 1
                        print(f"⚠️ Skipping current session directory: {temp_dir.name}")
                        continue
                    
                    # Extract timestamp from directory name
                    dir_timestamp = parse_timestamp_from_dirname(temp_dir.name)
                    
                    if dir_timestamp is None:
                        # Could not parse timestamp - skip this directory
                        skipped_unparseable += 1
                        print(f"⚠️ Skipping directory with unparseable name: {temp_dir.name}")
                        continue
                    
                    # Calculate age
                    age_seconds = time.time() - dir_timestamp
                    age_hours = age_seconds / 3600
                    age_minutes = age_seconds / 60
                    
                    # Check if directory is empty
                    is_empty = not any(temp_dir.iterdir())
                    
                    should_delete = False
                    reason = ""
                    
                    if is_empty and dir_timestamp < empty_cutoff_time:
                        # Empty folder older than empty_age_minutes
                        should_delete = True
                        reason = f"empty for {age_minutes:.1f} min"
                    elif dir_timestamp < cutoff_time:
                        # Any folder older than max_age_hours
                        should_delete = True
                        reason = f"age {age_hours:.1f} hours"
                    else:
                        skipped_active += 1
                    
                    if should_delete:
                        try:
                            shutil.rmtree(temp_dir)
                            cleaned_count += 1
                            print(f"✓ Cleaned up old temp directory: {temp_dir.name} ({reason})")
                        except Exception as e:
                            print(f"✗ Error removing old directory {temp_dir}: {e}")
                        
                except Exception as e:
                    print(f"✗ Error checking directory {temp_dir}: {e}")
        
        if cleaned_count > 0:
            print(f"✓ Cleaned up {cleaned_count} old session directories")
            if skipped_current > 0:
                print(f"  Protected current session directory")
            if skipped_active > 0:
                print(f"  Preserved {skipped_active} active directories")
        elif skipped_active > 0 or skipped_current > 0:
            print(f"✓ Cleanup check complete: {skipped_active} active sessions preserved, {skipped_current} current session protected")
        
        # Update the global cleanup timestamp
        update_cleanup_time()
            
    except BlockingIOError:
        # Another session is already running cleanup - skip silently
        print(f"⏭️ Cleanup already in progress by another session, skipping...")
        
    except Exception as e:
        print(f"✗ Error in cleanup_old_sessions: {e}")
        
    finally:
        # Release the lock if we acquired it
        if lock_file:
            try:
                fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
                lock_file.close()
            except Exception as e:
                print(f"✗ Error releasing lock: {e}")
