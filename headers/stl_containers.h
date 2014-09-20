


template <typename ValueType> class queue {

public:
	bool empty() const;
	size_type size() const;
	ValueType front();
	ValueType back();
	void push (const value_type& val);
	void pop();
	void swap (queue& x);


};


template <typename ValueType> class vector {
public:
	void assign (size_type n, const value_type& val);
	size_type size();
    size_type max_size();
    void      resize(size_type sz);
    size_type capacity() const noexcept;
    bool      empty() const noexcept;
    void      reserve(size_type n);
    void      shrink_to_fit();
    void push_back(const ValueType& x);
    void push_back(ValueType&& x);
    void pop_back();

    ValueType& operator[](size_type n);
    ValueType& back();

    iterator insert(const_iterator position, const ValueType& x);
    iterator insert(const_iterator position, ValueType&& x);
    iterator insert(const_iterator position, size_type n, const ValueType& x);
    iterator insert(const_iterator position, initializer_list<ValueType>);
 
    iterator erase(const_iterator position);
    iterator erase(const_iterator first, const_iterator last);
    void     swap(vector<ValueType,Allocator>&);
    void     clear() noexcept;
};


template <typename ValueType> class map {
public:
    ValueType& operator[](size_type n);
    bool empty();
    size_type size();

    iterator insert(const_iterator position, ValueType&& x);
    iterator insert(ValueType&& x);

    iterator  erase (const_iterator position);
    size_type erase (const key_type& k);
    iterator  erase (const_iterator first, const_iterator last);

    iterator find (const key_type& k);
    size_type count (const key_type& k);
};
