    _tasks.append(asyncio.create_task(db_flush_loop()))

    threading.Thread(target=run_web_server, daemon=True).start()
    logger.info("[Startup] ✅ همه تسک‌ها و وب‌سرور شروع شدن")

async def post_shutdown(application):
    for task in _tasks:
        try: task.cancel()
        except Exception: pass
    try: flush_db_sync()            # آخرین تغییرات حتماً روی دیسک نوشته بشن
    except Exception as e: logger.error(f"[Shutdown] flush: {e}")
    release_lock()

async def error_handler(update, ctx):
    await report_error("handler", ctx.error)

if __name__ == "__main__":
    if TOKEN == "PASTE_NEW_TOKEN_HERE":
        sys.exit("❌ توکن تنظیم نشده! متغیر محیطی BOT_TOKEN رو بساز (یا توکن جدید رو جای PASTE_NEW_TOKEN_HERE بذار).")
    acquire_lock()
    app = (
        Application.builder()
        .token(TOKEN)
        .base_url(BASE_URL)
        .post_init(post_init)
        .post_shutdown(post_shutdown)
        .build()
    )
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reset", reset_raffles))
    app.add_handler(CommandHandler("resetall", reset_users))
    app.add_handler(CommandHandler("backup", manual_backup))
    app.add_handler(CommandHandler("restore", restore_db))
    app.add_handler(CommandHandler("verify", verify_cmd))
    app.add_handler(CallbackQueryHandler(check_join_cb, pattern="^check_join$"))
    app.add_handler(CallbackQueryHandler(button_handler))