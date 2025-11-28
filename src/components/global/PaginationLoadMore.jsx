import React from 'react';
import { ChevronDown } from 'lucide-react';
import './PaginationLoadMore.css';

const PaginationLoadMore = ({ onLoadMore, isLoading }) => {
    return (
        <div className="pagination-container">
            <button
                className="load-more-btn"
                onClick={onLoadMore}
                disabled={isLoading}
            >
                {isLoading ? 'Loading...' : (
                    <>
                        <span>Load More</span>
                        <ChevronDown size={16} />
                    </>
                )}
            </button>
        </div>
    );
};

export default PaginationLoadMore;
