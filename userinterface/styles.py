def load_css():

    return """
<style>

/* ---------- Main Page ---------- */

.main .block-container{

    max-width: 950px;

    padding-top: 2rem;

    padding-bottom: 8rem;

}

/* ---------- Logo ---------- */

.logo{

    text-align:center;

    font-size:70px;

    margin-top:20px;

}

/* ---------- Title ---------- */

.title{

    text-align:center;

    font-size:42px;

    font-weight:700;

    margin-top:10px;

}

/* ---------- Subtitle ---------- */

.subtitle{

    text-align:center;

    color:#8d8d8d;

    font-size:20px;

    margin-bottom:40px;

}

/* ---------- Chat Messages ---------- */

.stChatMessage{

    border-radius:18px;

    padding:15px;

    margin-bottom:12px;

}

/* ---------- Chat Input ---------- */

.stChatInput{

    position:fixed;

    bottom:75px;

    left:50%;

    transform:translateX(-50%);

    width:65%;

    z-index:999;

}

/* ---------- Bottom Toolbar ---------- */

.bottom-toolbar{

    position:fixed;

    bottom:18px;

    left:50%;

    transform:translateX(-50%);

    width:65%;

    display:flex;

    justify-content:center;

    align-items:center;

    gap:15px;

    z-index:999;

}

/* ---------- Sidebar ---------- */

section[data-testid="stSidebar"]{

    width:290px !important;

}

/* ---------- Sidebar Buttons ---------- */

.stSidebar button{

    width:100%;

    border-radius:10px;

}

/* ---------- Expanders ---------- */

details{

    border-radius:12px;

}

/* ---------- File Uploader ---------- */

[data-testid="stFileUploader"]{

    width:220px;

}

/* ---------- Scrollbar ---------- */

::-webkit-scrollbar{

    width:8px;

}

::-webkit-scrollbar-thumb{

    border-radius:20px;

    background:#bfbfbf;

}

/* ---------- Footer ---------- */

footer{

    visibility:hidden;

}

header{

    visibility:hidden;

}

/* ---------- Top Padding ---------- */

.block-container{

    padding-top:2rem;

}

</style>
"""