import React from 'react'
import './Modal.css'
import DButton from '../atoms/DButton';

function Modal({
    openModal,
    setOpenModal,
    height,
    width,
    modalName,
    children
}) {
    if (!openModal) return null;

    return (
        <>
            <div className="fixed inset-0 flex items-center justify-center" style={{
                height: "100vh",
                width: "100vw",
                
                backgroundColor: "var(--dialog-bg)",
            }}>
                <div className="modal-container" style={{
                    height: height ? height : "50vh",
                    width: width ? width : "50vw",
                    borderRadius: "10px",
                }}>
                    <div className="modal-header">
                        <div className="modal-name">{modalName}</div>
                        <div style={{
                            display:"flex",
                            justifyContent:"center",
                            alignItems:"center",
                            right:0,
                            top:0,
                            padding:"5px"
                        }}>
                            <DButton
                                text="X"
                                onClick={() => setOpenModal(false)}
                                buttonClass={"button-close"}
                            />
                        </div> 
                    </div>
              <div style={{ 
                flexGrow: 1 ,
                height:"100%",
                width:"100%",
                display:"flex",
                justifyContent:"center",
                alignItems:"center",
               }}>
                    {children}
                    </div> 
                </div>
            </div>

        </>
    )
}

export default Modal
