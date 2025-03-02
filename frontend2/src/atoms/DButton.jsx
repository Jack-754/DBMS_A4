import React, {useState} from "react";

const DButton = (
    {text, onClick, buttonClass=''}
) => {
    return (
        <button
            onClick={onClick}
            className={`${buttonClass}`}
        >
            {text}
        </button>
    )
}

export default DButton;