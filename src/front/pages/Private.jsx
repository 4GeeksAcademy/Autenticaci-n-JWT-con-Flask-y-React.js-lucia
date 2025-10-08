import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import useGlobalReducer from "../hooks/useGlobalReducer";

export const Private = () => {
    const { store, dispatch } = useGlobalReducer();
    const [loading, setLoading] = useState(true);
    const [privateData, setPrivateData] = useState(null);
    const navigate = useNavigate();

    useEffect(() => {
        validateToken();
    }, []);

    const validateToken = async () => {
        try {
            const token = sessionStorage.getItem('token');

            // If no token, redirect to login
            if (!token) {
                navigate("/login");
                return;
            }

            const backendUrl = import.meta.env.VITE_BACKEND_URL;
            
            if (!backendUrl) {
                throw new Error("VITE_BACKEND_URL is not defined in .env file");
            }

            // Validate token with backend
            const response = await fetch(`${backendUrl}/api/token/validate`, {
                method: "GET",
                headers: {
                    "Authorization": `Bearer ${token}`
                }
            });

            const data = await response.json();

            if (!response.ok) {
                // Token is invalid, remove it and redirect to login
                sessionStorage.removeItem('token');
                dispatch({ type: "logout" });
                navigate("/login");
                return;
            }

            // Token is valid, update user in store
            dispatch({
                type: "set_user",
                payload: data.user
            });

            // Fetch private data
            const privateResponse = await fetch(`${backendUrl}/api/private`, {
                method: "GET",
                headers: {
                    "Authorization": `Bearer ${token}`
                }
            });

            const privateData = await privateResponse.json();
            setPrivateData(privateData);

        } catch (error) {
            console.error("Error validating token:", error);
            navigate("/login");
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="container mt-5 text-center">
                <div className="spinner-border text-primary" role="status">
                    <span className="visually-hidden">Loading...</span>
                </div>
                <p className="mt-3">Validating authentication...</p>
            </div>
        );
    }

    return (
        <div className="container mt-5">
            <div className="row justify-content-center">
                <div className="col-md-8">
                    <div className="card">
                        <div className="card-body">
                            <h2 className="card-title text-center mb-4">
                                🔒 Private Area
                            </h2>
                            
                            <div className="alert alert-success" role="alert">
                                <h4 className="alert-heading">Welcome!</h4>
                                <p>You have successfully accessed the private area.</p>
                                <hr />
                                <p className="mb-0">
                                    This page is only accessible to authenticated users.
                                </p>
                            </div>

                            {store.user && (
                                <div className="card mb-3">
                                    <div className="card-body">
                                        <h5 className="card-title">User Information</h5>
                                        <p className="card-text">
                                            <strong>Email:</strong> {store.user.email}
                                        </p>
                                        <p className="card-text">
                                            <strong>User ID:</strong> {store.user.id}
                                        </p>
                                    </div>
                                </div>
                            )}

                            {privateData && (
                                <div className="alert alert-info" role="alert">
                                    <strong>Message from server:</strong> {privateData.msg}
                                </div>
                            )}

                            <div className="text-center mt-4">
                                <p className="text-muted">
                                    This content is protected and requires authentication.
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};