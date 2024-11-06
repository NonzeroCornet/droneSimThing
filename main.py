import tkinter as tk


def on_run():
    root.destroy()
    # import run
    print("Haven't implemented run yet!")
    # run.main()
    return


def on_create():
    root.destroy()
    import create

    create.main()
    return


root = tk.Tk()
root.title("")
root.geometry("320x180")
root.resizable(False, False)
run_button = tk.Button(root, text="Run", command=on_run, height=4, width=15)
run_button.place(relx=0.25, rely=0.5, anchor=tk.CENTER)
create_button = tk.Button(root, text="Create", command=on_create, height=4, width=15)
create_button.place(relx=0.75, rely=0.5, anchor=tk.CENTER)
root.protocol("WM_DELETE_WINDOW", root.quit)
root.mainloop()
