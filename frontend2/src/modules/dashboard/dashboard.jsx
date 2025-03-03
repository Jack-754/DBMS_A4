import React, { useState, useEffect } from 'react';
// import ExpenseCard from '../expenses/ExpenseCard';
// import MyLineChart from '../graph/Graph';
// import MyPieChart from '../graph/Chart';
// import { callAPI } from '../../services/ApiHelper';
import DDropdown from '../../atoms/DDropdown';
import DButton from '../../atoms/DButton';
import Loader from '../../molecules/Loader';
import DataTable from '../../components/DataTable';
// import MyPieChart2 from '../graph/Chart2';
import './dashboard.css';

function Dashboard() {
    const [totalExpense, setTotalExpense] = useState(0);
    const [remainingBudget, setRemainingBudget] = useState(0);
    const [piedata2, setPiedata2] = useState([])
    let piedata = [
        { name: 'Remaining', value: remainingBudget },
        { name: 'Used', value: totalExpense },
    ];

    const [graphType, setGraphType] = useState('Present Week');
    const [graphData, setGraphData] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [categoryData, setCategoryData] = useState({});

    // Calculate the total spent by summing up the 'spent' field from all expenses
    // const totalSpent = expensesData.reduce((total, expense) => total + expense.spent, 0);

    const fetchGraphData = async () => {
        setIsLoading(true);
        let graph_type = graphType === 'Present Week' ? 'weekly' : 'monthly';
        const response = await callAPI('/expenses/daily', 'GET', {}, { type: graph_type });
        if (response.data && response.data.length > 0) {
            setGraphData(response.data);
        }
        setIsLoading(false);
    }

    const fetchPaymentData = async () => {
        setIsLoading(true);
        let graph_type = graphType === 'Present Week' ? 'weekly' : 'monthly';
        const response = await callAPI('/expenses/payment_method', 'GET', {}, {type: graph_type});
        if (response.data && response.data.length > 0) {
            setPiedata2(response.data);
        }
        setIsLoading(false);
    }

    const fetchCategoryData = async () => {
        setIsLoading(true);
        let graph_type = graphType === 'Present Week' ? 'weekly' : 'monthly';
        const response = await callAPI('/expenses/category', 'GET', {}, { type: graph_type });
        if (response.data) {
            // console.log('response',response.data);
            setCategoryData(response.data);
            const totalExp = response.data.total_amount;
            const totalBudget = response.data.total_budget;
            const remainingBudget = totalBudget >= totalExp ? totalBudget - totalExp : 0;
            console.log("###", totalExp, totalBudget, remainingBudget);
            setTotalExpense(totalExp);
            setRemainingBudget(remainingBudget);
            console.log("###", response);
        }
        // console.log('category',categoryData);
        setIsLoading(false);
    }

    useEffect(() => {
        fetchGraphData();
        fetchCategoryData();
        fetchPaymentData();
    }, [graphType]);

    const [showInput, setShowInput] = useState(false);

    const handleBudgetChange = async (newBudget) => {
        setIsLoading(true);
        const response = await callAPI('/expenses/setbudget', 'POST', { }, { budget: newBudget });
        await fetchCategoryData();
        setShowInput(false);
        setIsLoading(false);
    }

    if (isLoading) {
        return <Loader />
    }

    return (
        <div className="dashboard-container">
            <h1>Dashboard</h1>
            <DataTable />
        </div>
    );
}

export default Dashboard;
