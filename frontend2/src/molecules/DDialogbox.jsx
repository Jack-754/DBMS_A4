import React from "react";
import { useState } from "react";
import DButton from "../atoms/DButton";
import Modal from "../molecules/Modal";

function DDialogbox({message, class_name, func}){
    const [isDialogOpen, setIsDialogOpen] = useState(true);
    return (
        <Modal openModal={isDialogOpen} setOpenModal={setIsDialogOpen} height="30%" width="30%">
            <div style={{
                display: "flex",
                flexDirection: "column",
                justifyContent: "center",
                alignItems: "center",
                gap: "20px",
                height: "100%",
            }}>
            <div style={{
                textAlign: "center",
                fontSize: "40px",
                
            }}>
                {message}
            </div>
            <div style={{
                display: "flex",
                flexDirection: "row",
                justifyContent: "space-evenly",
                alignItems: "center",
                height: "50%",
                gap: "30px",
            }}>
                <div>
                <DButton text="OK" onClick={func} buttonClass="edit-btn-primary" />
                </div>
                <DButton text="Cancel" onClick={() => setIsDialogOpen(false)} buttonClass="delete-btn-primary" />
            </div>
            </div>
            
        </Modal>
    )
}

export default DDialogbox